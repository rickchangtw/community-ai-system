# Phase 6: Deployment Architecture

## Completed Time
2026-07-18

## Status
✅ Completed

## Description
Complete deployment architecture with Docker Compose for multi-agent orchestration.

## Architecture Overview

### Services (12 total)
| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| PostgreSQL | community-postgres | 5432 | Database |
| Redis | community-redis | 6379 | Event Bus & Caching |
| CEO Agent | ceo-agent | 3001 | Main Orchestrator |
| Property Agent | property-agent | 3002 | Property Management |
| Security Agent | security-agent | 3003 | Security Management |
| Fire Agent | fire-agent | 3004 | Fire Safety |
| Energy Agent | energy-agent | 3005 | Energy Management |
| Notice Agent | notice-agent | 3006 | Notice Center |
| Line Bot | line-bot | 3021 | LINE Webhook |
| Meeting Transcription | meeting-transcription | 3011 | Realtime Meeting |
| Monitoring Agent | monitoring-agent | 3010 | System Monitoring |
| Health Check | health-check | 3000 | Health Endpoint |

### Dependencies
- **PostgreSQL 16**: Database with schema initialization
- **Redis 7**: Message queue and caching
- **Python 3.12**: Runtime for all agents

## Deployment Files

### Docker Compose
- `01-docker-compose.yml` - Main deployment configuration

### Agent Dockerfiles
- `agents/ceo-agent/Dockerfile` - CEO Agent
- `agents/property-agent/Dockerfile` - Property Agent
- `agents/security-agent/Dockerfile` - Security Agent
- `agents/fire-agent/Dockerfile` - Fire Safety Agent
- `agents/energy-agent/Dockerfile` - Energy Agent
- `agents/notice-agent/Dockerfile` - Notice Center Agent
- `agents/monitoring-agent/Dockerfile` - Monitoring Agent
- `agents/line-bot/Dockerfile` - Line Bot
- `agents/scripts/Dockerfile` - Meeting Transcription

### Scripts
- `deploy.sh` - Automated deployment script
- `start.sh` - Quick start script
- `.env.example` - Environment variable template

## Deployment Steps

### 1. Clone Repository
```bash
cd /home/rick/shared-wiki/phase6
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and fill in Line Bot credentials
```

### 3. Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Verify
```bash
docker-compose ps
# All services should show "Running"
```

### 5. Access
```bash
# Line Bot
curl http://localhost:3021/health

# Health Check
curl http://localhost:3000

# CEO Agent
curl http://localhost:3001

# View Logs
docker-compose logs -f
```

## Service Health Check

### Check All Services
```bash
docker-compose ps
```

### Check PostgreSQL
```bash
docker-compose exec postgres pg_isready -U hermes -d community
```

### Check Redis
```bash
docker-compose exec redis redis-cli ping
```

### Check CEO Agent
```bash
curl http://localhost:3001/health
```

## Environment Variables

### Required
- `LINE_WEBHOOK_SECRET` - LINE Webhook secret
- `LINE_CHANNEL_SECRET` - LINE Channel secret
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Channel access token

### Optional
- `JWT_SECRET` - JWT secret for agent authentication
- `JWT_EXPIRY` - JWT token expiry (seconds)

## Port Allocation

### Agents
- 3001: CEO Agent
- 3002: Property Agent
- 3003: Security Agent
- 3004: Fire Safety Agent
- 3005: Energy Agent
- 3006: Notice Center Agent

### Services
- 3000: Health Check
- 3010: Monitoring Agent
- 3011: Meeting Transcription
- 3021: Line Bot

### Infrastructure
- 5432: PostgreSQL
- 6379: Redis

## Database Schema

### Tables (35 total)
- `communities` - Community master data
- `buildings` - Buildings
- `floors` - Floors
- `residents` - Residents
- `agent_roles` - Agent roles
- `agent_instances` - Agent instances
- `events` - Events
- `meetings` - Meetings
- `notices` - Notices
- `fee_records` - Fee records
- `work_orders` - Work orders
- `fire_equipment` - Fire equipment
- `energy_devices` - Energy devices
- `audit_logs` - Audit logs

## Monitoring

### Grafana Dashboard
- Access: http://localhost:3000
- Metrics: Agent heartbeat, message count, latency, error rate

### Log Files
- Each service logs to stdout/stderr
- Use `docker-compose logs <service>` to view logs

### Health Endpoints
- CEO Agent: http://localhost:3001/health
- Property Agent: http://localhost:3002/health
- Security Agent: http://localhost:3003/health
- Fire Agent: http://localhost:3004/health
- Energy Agent: http://localhost:3005/health
- Notice Agent: http://localhost:3006/health
- Line Bot: http://localhost:3021/health

## Troubleshooting

### Service Not Starting
```bash
# Check logs
docker-compose logs <service>

# Rebuild service
docker-compose build <service>

# Restart service
docker-compose restart <service>
```

### Database Connection Error
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database is ready
docker-compose exec postgres pg_isready -U hermes -d community
```

### Redis Connection Error
```bash
# Check Redis logs
docker-compose logs redis

# Verify Redis is running
docker-compose exec redis redis-cli ping
```

### Agent Not Responding
```bash
# Check agent logs
docker-compose logs ceo-agent

# Restart agent
docker-compose restart ceo-agent

# Verify port is listening
netstat -tlnp | grep 3001
```

## Backup Strategy

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U hermes community > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U hermes -d community < backup_20260718.sql
```

### Redis Backup
```bash
# Create backup
docker-compose exec redis redis-cli BGSAVE

# Copy snapshot
docker cp community-redis:/data/dump.rdb /backup/dump.rdb
```

## Scaling

### Horizontal Scaling
```bash
# Scale CEO Agent to 2 instances
docker-compose up -d --scale ceo-agent=2
```

### Resource Limits
```yaml
# In docker-compose.yml
services:
  ceo-agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Security

### Authentication
- JWT Token for agent-to-agent communication
- RBAC for database access control

### Encryption
- AES-256 for sensitive data
- TLS for communications (configure nginx)

### Audit Logging
- All operations logged to `audit_logs` table
- Log retention policy: 90 days

## Next Steps

### Phase 7: Integration Testing
- Test agent-to-agent communication
- Test event triggers
- Test notification routing
- Test database operations

### Phase 8: Performance Optimization
- Database indexing optimization
- Redis caching strategy
- Agent processing optimization
- Load testing

### Phase 9: Production Deployment
- Domain configuration
- SSL/TLS setup
- Backup automation
- Monitoring setup
- CI/CD pipeline
