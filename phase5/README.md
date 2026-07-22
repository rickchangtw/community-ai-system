# Phase 5: Agent Communication Protocol Design

## Completed Time
2026-07-18

## Status
✅ Completed

## Description
Design complete communication protocol for 6 Agent roles with event triggers, notification routing, and database integration.

## Communication Architecture

### Layers
- **Agent-to-Agent**: REST API (HTTP/1.1), ports 3001-3006
- **Agent-to-Line**: LINE Webhook API, port 3021
- **Agent-to-Database**: psycopg2, port 5432
- **Event Bus**: Redis message queue, port 6379

### Agent Roles and Ports
| Role | Port | Priority | Capabilities |
|------|------|----------|--------------|
| CEO | 3001 | 100 | Decision, Coordination, Authorization, Conflict Resolution |
| Property | 3002 | 90 | Facility Management, Fee Collection, Work Orders, Cleaning |
| Security | 3003 | 85 | Patrol Management, Visitor Management, Security Events, CCTV |
| Fire | 3004 | 80 | Fire Equipment, Emergency Notification, Drill Management |
| Energy | 3005 | 75 | Energy Monitoring, Device Management, Energy Saving Policies |
| Notice | 3006 | 70 | Announcement Publishing, Message Push, Notice Management |

## Message Format

### Schema
- Headers: message_id, timestamp, source_role, target_role, priority, community_id, event_id, expires_at
- Body: type, payload, metadata

### Message Types
- event_notification: Event notification with severity, affected residents
- task_assignment: Task assignment with deadline, priority
- task_update: Task status update
- decision: Decision notification with rationale
- data_sync: Data synchronization (insert/update/delete)
- alert: Alert with severity (1-4), recommended action
- report: Periodic report with recommendations
- confirmation: Confirmation (confirmed/rejected/acknowledged)

## Event Triggers

### Security Incident
- CEO: notification (priority 100)
- Security: handle (priority 85)
- Property: investigate (priority 90)

### Fire Alarm
- Fire: handle (priority 80)
- CEO: notification (priority 100)
- Security: monitor (priority 85)
- Property: evacuate (priority 90)

### Emergency
- CEO: coordinate (priority 100)
- Security: secure (priority 85)
- Fire: emergency_response (priority 80)
- Property: manage (priority 90)
- Energy: power_management (priority 75)
- Notice: broadcast (priority 70)

## Notification Routing

### Types
- **Emergency** (priority 4): Immediate broadcast via LINE + Telegram
- **Important** (priority 3): Urgent notification via LINE (24h timeout)
- **Routine** (priority 2): Standard notification via LINE (48h timeout)
- **Informational** (priority 1): Batch notification via LINE (72h timeout)

### Severity-Based Routing
- severity >= 4: immediate_broadcast
- severity >= 3: urgent_notification
- severity >= 2: standard_notification
- severity < 2: batch_notification

### Line Templates
- emergency_alert: 🚨 Emergency Alert
- important_notice: 📢 Important Notice
- routine_update: 📋 Routine Update
- informational: ℹ️ Informational

## Agent-to-Agent Flow

### Request Flow
1. Source agent sends request
2. Message queued (agent-to-agent)
3. Target agent receives message
4. Target agent processes task
5. Target agent sends response
6. Source agent receives response

### Error Handling
- **Timeout**: Retry (max 3 retries, 30s interval)
- **Target offline**: Queue and notify CEO (24h timeout)
- **Conflict**: Escalate to CEO, notify affected roles

## Database Integration

### Rules
- Read own data: Agent can read its own data
- Write own data: Agent can write data it manages
- Cross-role read: Requires authorization
- Audit logging: All operations logged to audit_logs

### Examples
- **Event Handling**: security → events table → CEO query → assign → property update
- **Notification**: CEO → notices table → notice query → LINE API → notice update

## Port Allocation
- Agents: CEO=3001, Property=3002, Security=3003, Fire=3004, Energy=3005, Notice=3006
- Services: LINE=3021, Redis=6379, PostgreSQL=5432
- Health Check: 3000

## Security
- JWT Token authentication
- AES-256 encryption for sensitive data
- Audit logging for all operations
- RBAC access control
- HTTPS/TLS for communications

## Monitoring
- Agent heartbeat check (every 30 seconds)
- Message queue depth monitoring
- Processing latency monitoring
- Error rate monitoring
- Resource usage monitoring

## Files
- `01-communication-protocol.yaml` - Complete communication protocol design
- `README.md` - This documentation
