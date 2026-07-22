# Deployment Guide

## Quick Start

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

## Architecture

### Service Dependencies
```
PostgreSQL 16 (5432)
    ↓
Redis 7 (6379)
    ↓
CEO Agent (3001) ← Main Orchestrator
    ↓
Property Agent (3002)
Security Agent (3003)
Fire Agent (3004)
Energy Agent (3005)
Notice Agent (3006)
    ↓
Line Bot (3021) ← External Interface
```

### Communication Flow
1. User sends message to Line Bot (3021)
2. Line Bot validates and forwards to CEO Agent (3001)
3. CEO Agent coordinates with other agents
4. Agents communicate via Redis message queue
5. Agents update PostgreSQL database
6. Results sent back via Line Bot

## Database Schema

### Core Tables
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

### Health Check
```bash
curl http://localhost:3000
# Response: {"status": "ok", "message": "All services healthy"}
```

### Service Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs ceo-agent
docker-compose logs postgres
```

## Backup

### Database Backup
```bash
docker-compose exec postgres pg_dump -U hermes community > backup_$(date +%Y%m%d).sql
```

### Redis Backup
```bash
docker-compose exec redis redis-cli BGSAVE
docker cp community-redis:/data/dump.rdb /backup/dump.rdb
```

## Troubleshooting

### Service Not Starting
```bash
docker-compose logs <service>
docker-compose restart <service>
```

### Database Connection Error
```bash
docker-compose exec postgres pg_isready -U hermes -d community
```

### Redis Connection Error
```bash
docker-compose exec redis redis-cli ping
```

## Scaling

### Horizontal Scaling
```bash
docker-compose up -d --scale ceo-agent=2
```

### Resource Limits
```yaml
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
- TLS for communications

### Audit Logging
- All operations logged to `audit_logs` table
- Log retention: 90 days

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
