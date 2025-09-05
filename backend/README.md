# Krishi Sakhi - AI-Powered Personal Farming Assistant

A production-grade backend for Smart India Hackathon problem "AI-Powered Personal Farming Assistant for Kerala Farmers (Krishi Sakhi)".

## Problem Summary

Krishi Sakhi is an AI-powered personal farming assistant designed specifically for Kerala farmers. The system provides:

- **Farmer & Farm Profiling**: Comprehensive farmer and farm data management
- **Malayalam Conversational Interface**: Voice and text support in Malayalam and English
- **Activity Tracking**: Log farming activities from free-form text/voice inputs
- **Personalized Advisories**: Proactive farming advice based on weather, pest data, and best practices
- **Reminders & Alerts**: Smart scheduling and notification system
- **Knowledge Engine**: Local crop calendars, pest data, best practices, and price trends
- **Admin Operations**: Complete administrative interface with audit trails
- **Privacy Compliance**: India DPDP Act aligned data protection

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Portal    │    │   Admin Panel   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      FastAPI Backend      │
                    │  ┌─────────────────────┐  │
                    │  │   Auth & Security   │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Business Logic    │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Provider Layer    │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Data & Services       │
                    │  ┌─────────────────────┐  │
                    │  │   PostgreSQL 15     │  │
                    │  │ + PostGIS + pgvector│  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Redis Cache       │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Celery Workers    │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    External Services      │
                    │  ┌─────────────────────┐  │
                    │  │   Weather APIs      │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   ASR/TTS Services  │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Notification APIs │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### Setup

1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd krishi-sakhi
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**:
   ```bash
   make up
   ```

3. **Seed demo data**:
   ```bash
   make seed
   ```

4. **Access the application**:
   - API Documentation: http://localhost:8000/docs
   - Flower (Celery Monitor): http://localhost:5555
   - Admin Panel: http://localhost:8000/admin

## Make Targets

```bash
make up          # Start all services
make down        # Stop all services
make logs        # View logs
make fmt         # Format code
make lint        # Run linters
make test        # Run tests
make seed        # Seed demo data
make flower      # Open Flower dashboard
make clean       # Clean up containers and volumes
```

## API Examples

### Authentication

```bash
# Start OTP flow
curl -X POST "http://localhost:8000/auth/otp/start" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Verify OTP
curl -X POST "http://localhost:8000/auth/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{"req_id": "req_123", "code": "123456"}'
```

### Log Activity (Malayalam)

```bash
curl -X POST "http://localhost:8000/activities/log" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": 1,
    "field_id": 1,
    "text": "നാളെ തളിക്കൽ വേണ്ട"
  }'
```

### Generate Advisory

```bash
curl -X POST "http://localhost:8000/advisories/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": 1, "field_id": 1}'
```

### Knowledge Base Search

```bash
curl "http://localhost:8000/kb/search?q=വാഴ%20ഇലക്കീടം&top_k=5" \
  -H "Authorization: Bearer <token>"
```

## Demo Data

The seed script creates:

- **3 Demo Farmers** in different Kerala districts
- **Sample Farms & Fields** with various crops (paddy, banana, brinjal)
- **Knowledge Base Documents** including crop calendars and IPM guides
- **Sample Pest Reports** and price data
- **Weather Observations** for testing advisory generation

## Security & Privacy

### Threat Model

- **Authentication**: Phone-based OTP with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: PII encryption at rest, secure transmission
- **Rate Limiting**: OTP request throttling
- **Audit Logging**: Complete audit trail for all operations

### DPDP Compliance Checklist

- ✅ **Consent Management**: Explicit consent flags for data processing
- ✅ **Data Export**: Complete user data export functionality
- ✅ **Right to Deletion**: Secure data deletion with audit trail
- ✅ **Data Minimization**: Only collect necessary data
- ✅ **Purpose Limitation**: Clear data usage purposes
- ✅ **Storage Limitation**: Automatic data retention policies
- ✅ **Security Safeguards**: Encryption, access controls, monitoring

## Development

### Code Standards

- **Python 3.10+** with type hints
- **FastAPI** for API framework
- **SQLAlchemy 2.x** for ORM
- **Pydantic v2** for data validation
- **Ruff + Black** for code formatting
- **MyPy** for type checking

### Testing

```bash
make test              # Run all tests
make test-coverage     # Run with coverage report
make test-integration  # Run integration tests
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Production Checklist

- [ ] Configure production environment variables
- [ ] Set up SSL certificates
- [ ] Configure external service keys
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategies
- [ ] Review security settings
- [ ] Load test the application

### Environment Variables

See `.env.example` for all required configuration options.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is developed for Smart India Hackathon 2024.

## Support

For technical support or questions, please contact the development team or create an issue in the repository.
