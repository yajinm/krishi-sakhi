"""
User data export script for privacy compliance.

Exports all user data in JSON format for DPDP Act compliance.
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import AsyncSessionLocal
from app.models import (
    Activity,
    Advisory,
    AuditLog,
    Consent,
    Farmer,
    Farm,
    Field,
    Media,
    Notification,
    Reminder,
    User,
)

app = typer.Typer(help="Export user data for privacy compliance")


async def get_user_data(session: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
    """Get all user data for export."""
    
    # Get user
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Get farmer data
    farmer_result = await session.execute(select(Farmer).where(Farmer.user_id == user_id))
    farmer = farmer_result.scalar_one_or_none()
    
    # Get farms
    farms = []
    if farmer:
        farms_result = await session.execute(select(Farm).where(Farm.farmer_id == farmer.id))
        farms = farms_result.scalars().all()
    
    # Get fields
    fields = []
    if farms:
        farm_ids = [farm.id for farm in farms]
        fields_result = await session.execute(select(Field).where(Field.farm_id.in_(farm_ids)))
        fields = fields_result.scalars().all()
    
    # Get activities
    activities = []
    if farmer:
        activities_result = await session.execute(
            select(Activity).where(Activity.farmer_id == farmer.id)
        )
        activities = activities_result.scalars().all()
    
    # Get media
    media = []
    if activities:
        activity_ids = [activity.id for activity in activities]
        media_result = await session.execute(
            select(Media).where(Media.activity_id.in_(activity_ids))
        )
        media = media_result.scalars().all()
    
    # Get advisories
    advisories = []
    if farmer:
        advisories_result = await session.execute(
            select(Advisory).where(Advisory.farmer_id == farmer.id)
        )
        advisories = advisories_result.scalars().all()
    
    # Get reminders
    reminders = []
    if farmer:
        reminders_result = await session.execute(
            select(Reminder).where(Reminder.farmer_id == farmer.id)
        )
        reminders = reminders_result.scalars().all()
    
    # Get notifications
    notifications = []
    if farmer:
        notifications_result = await session.execute(
            select(Notification).where(Notification.farmer_id == farmer.id)
        )
        notifications = notifications_result.scalars().all()
    
    # Get consents
    consents_result = await session.execute(select(Consent).where(Consent.user_id == user_id))
    consents = consents_result.scalars().all()
    
    # Get audit logs
    audit_logs_result = await session.execute(select(AuditLog).where(AuditLog.user_id == user_id))
    audit_logs = audit_logs_result.scalars().all()
    
    # Compile user data
    user_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "app_version": settings.app_version,
            "data_retention_days": settings.data_retention_days,
        },
        "user": {
            "id": str(user.id),
            "phone": user.phone,
            "role": user.role.value,
            "locale": user.locale,
            "consent_flags": user.consent_flags,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        },
        "farmer": {
            "id": str(farmer.id),
            "name": farmer.name,
            "district": farmer.district,
            "panchayat": farmer.panchayat,
            "village": farmer.village,
            "lat": farmer.lat,
            "lon": farmer.lon,
            "soil_type": farmer.soil_type.value if farmer.soil_type else None,
            "irrig_src": farmer.irrig_src.value if farmer.irrig_src else None,
            "experience_years": farmer.experience_years,
            "farm_size_ha": farmer.farm_size_ha,
            "primary_crops": farmer.primary_crops,
            "farming_method": farmer.farming_method,
            "education_level": farmer.education_level,
            "annual_income": farmer.annual_income,
            "family_size": farmer.family_size,
            "is_active": farmer.is_active,
            "created_at": farmer.created_at.isoformat(),
            "updated_at": farmer.updated_at.isoformat(),
        } if farmer else None,
        "farms": [
            {
                "id": str(farm.id),
                "name": farm.name,
                "area_ha": farm.area_ha,
                "description": farm.description,
                "is_active": farm.is_active,
                "created_at": farm.created_at.isoformat(),
                "updated_at": farm.updated_at.isoformat(),
            }
            for farm in farms
        ],
        "fields": [
            {
                "id": str(field.id),
                "farm_id": str(field.farm_id),
                "name": field.name,
                "crop": field.crop,
                "variety": field.variety,
                "sow_date": field.sow_date.isoformat() if field.sow_date else None,
                "area_ha": field.area_ha,
                "is_active": field.is_active,
                "created_at": field.created_at.isoformat(),
                "updated_at": field.updated_at.isoformat(),
            }
            for field in fields
        ],
        "activities": [
            {
                "id": str(activity.id),
                "field_id": str(activity.field_id) if activity.field_id else None,
                "timestamp": activity.timestamp.isoformat(),
                "kind": activity.kind.value if activity.kind else None,
                "text_raw": activity.text_raw,
                "text_processed": activity.text_processed,
                "data_json": activity.data_json,
                "language": activity.language,
                "confidence_score": activity.confidence_score,
                "is_verified": activity.is_verified,
                "created_at": activity.created_at.isoformat(),
                "updated_at": activity.updated_at.isoformat(),
            }
            for activity in activities
        ],
        "media": [
            {
                "id": str(media.id),
                "activity_id": str(media.activity_id),
                "media_type": media.media_type.value,
                "filename": media.filename,
                "original_filename": media.original_filename,
                "file_path": media.file_path,
                "file_size": media.file_size,
                "mime_type": media.mime_type,
                "duration_seconds": media.duration_seconds,
                "width": media.width,
                "height": media.height,
                "metadata": media.metadata,
                "is_processed": media.is_processed,
                "created_at": media.created_at.isoformat(),
                "updated_at": media.updated_at.isoformat(),
            }
            for media in media
        ],
        "advisories": [
            {
                "id": str(advisory.id),
                "field_id": str(advisory.field_id) if advisory.field_id else None,
                "timestamp": advisory.timestamp.isoformat(),
                "title": advisory.title,
                "text": advisory.text,
                "text_ml": advisory.text_ml,
                "severity": advisory.severity.value,
                "tags": advisory.tags,
                "source": advisory.source.value,
                "source_data": advisory.source_data,
                "is_acknowledged": advisory.is_acknowledged,
                "acknowledged_at": advisory.acknowledged_at.isoformat() if advisory.acknowledged_at else None,
                "is_read": advisory.is_read,
                "read_at": advisory.read_at.isoformat() if advisory.read_at else None,
                "is_active": advisory.is_active,
                "expires_at": advisory.expires_at.isoformat() if advisory.expires_at else None,
                "created_at": advisory.created_at.isoformat(),
                "updated_at": advisory.updated_at.isoformat(),
            }
            for advisory in advisories
        ],
        "reminders": [
            {
                "id": str(reminder.id),
                "field_id": str(reminder.field_id) if reminder.field_id else None,
                "kind": reminder.kind.value,
                "title": reminder.title,
                "text": reminder.text,
                "text_ml": reminder.text_ml,
                "due_ts": reminder.due_ts.isoformat(),
                "recur_cron": reminder.recur_cron,
                "is_recurring": reminder.is_recurring,
                "is_paused": reminder.is_paused,
                "priority": reminder.priority,
                "metadata": reminder.metadata,
                "is_active": reminder.is_active,
                "created_at": reminder.created_at.isoformat(),
                "updated_at": reminder.updated_at.isoformat(),
            }
            for reminder in reminders
        ],
        "notifications": [
            {
                "id": str(notification.id),
                "reminder_id": str(notification.reminder_id) if notification.reminder_id else None,
                "channel": notification.channel.value,
                "recipient": notification.recipient,
                "title": notification.title,
                "message": notification.message,
                "message_ml": notification.message_ml,
                "payload_json": notification.payload_json,
                "status": notification.status.value,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "error_message": notification.error_message,
                "retry_count": notification.retry_count,
                "max_retries": notification.max_retries,
                "provider_response": notification.provider_response,
                "is_active": notification.is_active,
                "created_at": notification.created_at.isoformat(),
                "updated_at": notification.updated_at.isoformat(),
            }
            for notification in notifications
        ],
        "consents": [
            {
                "id": str(consent.id),
                "kind": consent.kind.value,
                "granted": consent.granted,
                "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
                "purpose": consent.purpose,
                "purpose_ml": consent.purpose_ml,
                "legal_basis": consent.legal_basis,
                "retention_period": consent.retention_period,
                "third_parties": consent.third_parties,
                "conditions": consent.conditions,
                "version": consent.version,
                "is_active": consent.is_active,
                "created_at": consent.created_at.isoformat(),
                "updated_at": consent.updated_at.isoformat(),
            }
            for consent in consents
        ],
        "audit_logs": [
            {
                "id": str(audit_log.id),
                "action": audit_log.action.value,
                "target_type": audit_log.target_type,
                "target_id": str(audit_log.target_id) if audit_log.target_id else None,
                "resource": audit_log.resource,
                "ip_address": audit_log.ip_address,
                "user_agent": audit_log.user_agent,
                "session_id": audit_log.session_id,
                "request_id": audit_log.request_id,
                "timestamp": audit_log.timestamp.isoformat(),
                "success": audit_log.success,
                "error_message": audit_log.error_message,
                "metadata": audit_log.metadata,
                "created_at": audit_log.created_at.isoformat(),
            }
            for audit_log in audit_logs
        ],
    }
    
    return user_data


@app.command()
def export_user_data(
    user_id: str = typer.Argument(..., help="User ID to export data for"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty print JSON"),
):
    """Export all user data for privacy compliance."""
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        typer.echo(f"❌ Invalid user ID: {user_id}")
        raise typer.Exit(1)
    
    async def _export():
        async with AsyncSessionLocal() as session:
            try:
                typer.echo(f"📊 Exporting data for user {user_id}...")
                
                user_data = await get_user_data(session, user_uuid)
                
                # Generate output filename if not provided
                if not output_file:
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    output_file = f"user_data_export_{user_id}_{timestamp}.json"
                
                # Write to file
                output_path = Path(output_file)
                with open(output_path, "w", encoding="utf-8") as f:
                    if pretty:
                        json.dump(user_data, f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(user_data, f, ensure_ascii=False)
                
                typer.echo(f"✅ User data exported to: {output_path}")
                typer.echo(f"   - File size: {output_path.stat().st_size / 1024:.1f} KB")
                typer.echo(f"   - Export timestamp: {user_data['export_info']['exported_at']}")
                
            except ValueError as e:
                typer.echo(f"❌ Error: {e}")
                raise typer.Exit(1)
            except Exception as e:
                typer.echo(f"❌ Unexpected error: {e}")
                raise typer.Exit(1)
    
    asyncio.run(_export())


@app.command()
def export_all_users(
    output_dir: str = typer.Option("./exports", "--output-dir", "-d", help="Output directory"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty print JSON"),
):
    """Export data for all users."""
    
    async def _export_all():
        async with AsyncSessionLocal() as session:
            try:
                typer.echo("📊 Exporting data for all users...")
                
                # Get all users
                users_result = await session.execute(select(User))
                users = users_result.scalars().all()
                
                if not users:
                    typer.echo("❌ No users found")
                    raise typer.Exit(1)
                
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                exported_count = 0
                for user in users:
                    try:
                        typer.echo(f"   Exporting user {user.id} ({user.phone})...")
                        
                        user_data = await get_user_data(session, user.id)
                        
                        # Generate filename
                        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                        filename = f"user_data_export_{user.id}_{timestamp}.json"
                        file_path = output_path / filename
                        
                        # Write to file
                        with open(file_path, "w", encoding="utf-8") as f:
                            if pretty:
                                json.dump(user_data, f, indent=2, ensure_ascii=False)
                            else:
                                json.dump(user_data, f, ensure_ascii=False)
                        
                        exported_count += 1
                        
                    except Exception as e:
                        typer.echo(f"   ❌ Failed to export user {user.id}: {e}")
                        continue
                
                typer.echo(f"✅ Exported data for {exported_count}/{len(users)} users")
                typer.echo(f"   Output directory: {output_path}")
                
            except Exception as e:
                typer.echo(f"❌ Unexpected error: {e}")
                raise typer.Exit(1)
    
    asyncio.run(_export_all())


if __name__ == "__main__":
    app()
