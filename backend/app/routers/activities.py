"""
Activities router.

Handles farming activity logging and retrieval.
"""

import uuid
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import CurrentUser, DatabaseSession, ActivityWritePermission
from app.models import Activity, ActivityKind, Farmer, Field, Media, MediaType
from app.providers import get_asr_provider, get_nlu_provider

router = APIRouter()


class ActivityLogRequest(BaseModel):
    """Request model for logging activity."""
    farmer_id: uuid.UUID = Field(..., description="Farmer ID")
    field_id: Optional[uuid.UUID] = Field(None, description="Field ID (optional)")
    text: Optional[str] = Field(None, description="Activity text in Malayalam or English")
    audio_url: Optional[str] = Field(None, description="Audio file URL for transcription")
    language: Optional[str] = Field("ml-IN", description="Language code")


class ActivityLogResponse(BaseModel):
    """Response model for activity logging."""
    id: uuid.UUID = Field(..., description="Activity ID")
    farmer_id: uuid.UUID = Field(..., description="Farmer ID")
    field_id: Optional[uuid.UUID] = Field(None, description="Field ID")
    timestamp: datetime = Field(..., description="Activity timestamp")
    kind: Optional[str] = Field(None, description="Detected activity kind")
    text_raw: Optional[str] = Field(None, description="Original text")
    text_processed: Optional[str] = Field(None, description="Processed text")
    language: Optional[str] = Field(None, description="Detected language")
    confidence_score: Optional[int] = Field(None, description="NLU confidence score")
    entities: Optional[dict] = Field(None, description="Extracted entities")
    created_at: datetime = Field(..., description="Creation timestamp")


class ActivityListResponse(BaseModel):
    """Response model for activity list."""
    activities: List[ActivityLogResponse] = Field(..., description="List of activities")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")


@router.post("/log", response_model=ActivityLogResponse)
async def log_activity(
    request: ActivityLogRequest,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    """
    Log a farming activity.
    
    Processes text or audio input to extract activity information and stores it.
    """
    # Verify farmer exists and user has access
    farmer_result = await session.execute(
        select(Farmer).where(Farmer.id == request.farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Check if user can access this farmer's data
    if current_user.role.value != "admin" and farmer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to farmer data"
        )
    
    # Verify field exists if provided
    if request.field_id:
        field_result = await session.execute(
            select(Field).where(Field.id == request.field_id)
        )
        field = field_result.scalar_one_or_none()
        
        if not field or field.farm.farmer_id != request.farmer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found or doesn't belong to farmer"
            )
    
    # Process text or audio
    text_to_process = request.text
    language = request.language
    
    if request.audio_url:
        # Transcribe audio
        asr_provider = get_asr_provider()
        transcription = await asr_provider.transcribe_url(request.audio_url, language)
        text_to_process = transcription["text"]
        language = transcription["language"]
    
    if not text_to_process:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either text or audio_url must be provided"
        )
    
    # Process with NLU
    nlu_provider = get_nlu_provider()
    nlu_result = await nlu_provider.process_text(text_to_process, language)
    
    # Map intent to activity kind
    intent_to_kind = {
        "log_activity": ActivityKind.OTHER,  # Will be refined based on entities
        "ask_kb": ActivityKind.OTHER,
        "request_advice": ActivityKind.OTHER,
        "smalltalk_other": ActivityKind.OTHER,
    }
    
    activity_kind = intent_to_kind.get(nlu_result["intent"], ActivityKind.OTHER)
    
    # Refine activity kind based on entities
    entities = nlu_result.get("entities", {})
    if "activity" in entities:
        activity_entity = entities["activity"][0].lower()
        if any(word in activity_entity for word in ["നടൽ", "plant", "sow"]):
            activity_kind = ActivityKind.SOWING
        elif any(word in activity_entity for word in ["വെള്ളം", "water", "irrigation"]):
            activity_kind = ActivityKind.IRRIGATION
        elif any(word in activity_entity for word in ["വളം", "fertilizer"]):
            activity_kind = ActivityKind.FERTILIZER
        elif any(word in activity_entity for word in ["കീടനാശിനി", "pesticide"]):
            activity_kind = ActivityKind.PESTICIDE
        elif any(word in activity_entity for word in ["വിളവെടുപ്പ്", "harvest"]):
            activity_kind = ActivityKind.HARVEST
    
    # Create activity record
    activity = Activity(
        farmer_id=request.farmer_id,
        field_id=request.field_id,
        kind=activity_kind,
        text_raw=request.text,
        text_processed=text_to_process,
        data_json={
            "intent": nlu_result["intent"],
            "entities": entities,
            "confidence": nlu_result["confidence"],
            "language": nlu_result["language"],
        },
        language=language,
        confidence_score=int(nlu_result["confidence"] * 100),
    )
    
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    
    return ActivityLogResponse(
        id=activity.id,
        farmer_id=activity.farmer_id,
        field_id=activity.field_id,
        timestamp=activity.timestamp,
        kind=activity.kind.value if activity.kind else None,
        text_raw=activity.text_raw,
        text_processed=activity.text_processed,
        language=activity.language,
        confidence_score=activity.confidence_score,
        entities=entities,
        created_at=activity.created_at,
    )


@router.get("/", response_model=ActivityListResponse)
async def list_activities(
    farmer_id: uuid.UUID = Query(..., description="Farmer ID"),
    field_id: Optional[uuid.UUID] = Query(None, description="Field ID filter"),
    from_date: Optional[datetime] = Query(None, description="Start date filter"),
    to_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: CurrentUser = Depends(ActivityReadPermission),
    session: DatabaseSession = Depends(),
):
    """
    List farming activities for a farmer.
    
    Returns paginated list of activities with optional filters.
    """
    # Verify farmer exists and user has access
    farmer_result = await session.execute(
        select(Farmer).where(Farmer.id == farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Check if user can access this farmer's data
    if current_user.role.value != "admin" and farmer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to farmer data"
        )
    
    # Build query
    query = select(Activity).where(Activity.farmer_id == farmer_id)
    
    if field_id:
        query = query.where(Activity.field_id == field_id)
    
    if from_date:
        query = query.where(Activity.timestamp >= from_date)
    
    if to_date:
        query = query.where(Activity.timestamp <= to_date)
    
    # Get total count
    count_query = select(Activity).where(Activity.farmer_id == farmer_id)
    if field_id:
        count_query = count_query.where(Activity.field_id == field_id)
    if from_date:
        count_query = count_query.where(Activity.timestamp >= from_date)
    if to_date:
        count_query = count_query.where(Activity.timestamp <= to_date)
    
    total_result = await session.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination and ordering
    query = query.order_by(desc(Activity.timestamp)).offset((page - 1) * size).limit(size)
    
    # Execute query
    result = await session.execute(query)
    activities = result.scalars().all()
    
    # Convert to response format
    activity_responses = []
    for activity in activities:
        entities = activity.data_json.get("entities", {}) if activity.data_json else {}
        
        activity_responses.append(ActivityLogResponse(
            id=activity.id,
            farmer_id=activity.farmer_id,
            field_id=activity.field_id,
            timestamp=activity.timestamp,
            kind=activity.kind.value if activity.kind else None,
            text_raw=activity.text_raw,
            text_processed=activity.text_processed,
            language=activity.language,
            confidence_score=activity.confidence_score,
            entities=entities,
            created_at=activity.created_at,
        ))
    
    return ActivityListResponse(
        activities=activity_responses,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{activity_id}", response_model=ActivityLogResponse)
async def get_activity(
    activity_id: uuid.UUID,
    current_user: CurrentUser = Depends(ActivityReadPermission),
    session: DatabaseSession = Depends(),
):
    """
    Get a specific activity by ID.
    
    Returns detailed information about a single activity.
    """
    # Get activity
    result = await session.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Check if user can access this activity
    if current_user.role.value != "admin" and activity.farmer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to activity data"
        )
    
    entities = activity.data_json.get("entities", {}) if activity.data_json else {}
    
    return ActivityLogResponse(
        id=activity.id,
        farmer_id=activity.farmer_id,
        field_id=activity.field_id,
        timestamp=activity.timestamp,
        kind=activity.kind.value if activity.kind else None,
        text_raw=activity.text_raw,
        text_processed=activity.text_processed,
        language=activity.language,
        confidence_score=activity.confidence_score,
        entities=entities,
        created_at=activity.created_at,
    )
