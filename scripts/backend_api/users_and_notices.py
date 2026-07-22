#!/usr/bin/env python3
"""FastAPI backend service for user management and notification system.

Provides RESTful API endpoints for managing community users, notifications,
and community information. Stores data in /tmp/community_data/ as JSON files
with thread-safe in-memory data stores.
"""

import json
import logging
import os
import threading
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uvicorn import Config, Server

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = "/tmp"
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("backend_api")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("/tmp/backend_api.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(file_handler)

# ── Data store path ──────────────────────────────────────────────────────────
DATA_DIR = "/tmp/community_data"
os.makedirs(DATA_DIR, exist_ok=True)


# ── Thread-safe in-memory stores ─────────────────────────────────────────────
_lock = threading.Lock()
_users: dict[str, dict] = {}
_notifications: list[dict] = []
_community: dict | None = None
_delivery_records: dict[str, list[dict]] = {}


# ── Pydantic models ──────────────────────────────────────────────────────────
class RegisterUserRequest(BaseModel):
    line_id: str
    name: str
    building: str
    unit: str


class SendNotificationRequest(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    target_roles: list[str] | None = None
    target_residents: list[str] | None = None


class CommunityInfoRequest(BaseModel):
    name: str
    address: str
    phone: str
    manager_name: str


# ── Helper ────────────────────────────────────────────────────────────────────
def _persist_users():
    """Persist users to JSON file."""
    path = os.path.join(DATA_DIR, "users.json")
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_users, f, ensure_ascii=False, indent=2)


def _persist_notifications():
    """Persist notifications to JSON file."""
    path = os.path.join(DATA_DIR, "notifications.json")
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_notifications, f, ensure_ascii=False, indent=2)


def _persist_community():
    """Persist community info to JSON file."""
    path = os.path.join(DATA_DIR, "community.json")
    with _lock:
        if _community:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(_community, f, ensure_ascii=False, indent=2)


def _generate_notice_id() -> str:
    """Generate a unique notice ID."""
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"notice_{now}"


def _generate_delivery_id() -> str:
    """Generate a unique delivery ID."""
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"delivery_{now}"


# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Community User & Notification API",
    description="Backend service for managing community users, notifications, and community info.",
    version="1.0.0",
)


# ── Middleware ────────────────────────────────────────────────────────────────
@app.middleware("http")
async def cors_middleware(request, call_next):
    """Add CORS headers for testing."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.options("/users/register")
@app.options("/notifications/send")
@app.options("/community")
async def options_handler(request):
    """Handle CORS preflight requests."""
    return Response(status_code=204)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ── Users ─────────────────────────────────────────────────────────────────────
@app.get("/users")
async def list_users():
    """List all registered users."""
    with _lock:
        users = _users.copy()
    logger.info("List users requested")
    return users


@app.get("/users/{line_id}")
async def get_user(line_id: str):
    """Get a user by LINE ID."""
    with _lock:
        user = _users.get(line_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found: {line_id}")
    logger.info(f"Get user requested: {line_id}")
    return user


@app.post("/users/register")
async def register_user(data: RegisterUserRequest):
    """Register a new user."""
    with _lock:
        if data.line_id in _users:
            logger.warning(f"User already registered: {data.line_id}")
            raise HTTPException(
                status_code=400, detail=f"User already registered: {data.line_id}"
            )
        user = {
            "line_id": data.line_id,
            "name": data.name,
            "building": data.building,
            "unit": data.unit,
            "registered_at": datetime.now().isoformat(),
        }
        _users[data.line_id] = user
    _persist_users()
    logger.info(f"User registered: {data.line_id} ({data.name})")
    return user


# ── Notifications ─────────────────────────────────────────────────────────────
@app.get("/notifications")
async def list_notifications():
    """List all notifications."""
    with _lock:
        items = _notifications.copy()
    logger.info("List notifications requested")
    return items


@app.get("/notifications/{notice_id}")
async def get_notification(notice_id: str):
    """Get a notification by ID."""
    with _lock:
        notice = next((n for n in _notifications if n.get("id") == notice_id), None)
    if notice is None:
        raise HTTPException(
            status_code=404, detail=f"Notification not found: {notice_id}"
        )
    logger.info(f"Get notification requested: {notice_id}")
    return notice


@app.post("/notifications/send")
async def send_notification(data: SendNotificationRequest):
    """Create and send a new notification."""
    with _lock:
        notice = {
            "id": _generate_notice_id(),
            "title": data.title,
            "content": data.content,
            "priority": data.priority,
            "target_roles": data.target_roles or [],
            "target_residents": data.target_residents or [],
            "sent_at": datetime.now().isoformat(),
            "delivery_status": "pending",
        }
        _notifications.append(notice)
        _delivery_records[notice["id"]] = []
    _persist_notifications()
    logger.info(
        f"Notification sent: {notice['id']} | priority={data.priority} | "
        f"targets={len(data.target_residents or [])}"
    )
    return notice


@app.get("/notifications/{notice_id}/deliveries")
async def get_deliveries(notice_id: str):
    """Get delivery records for a notification."""
    with _lock:
        deliveries = _delivery_records.get(notice_id, [])
    logger.info(f"Get deliveries requested: {notice_id}")
    return deliveries


# ── Community ─────────────────────────────────────────────────────────────────
@app.post("/community")
async def update_community(data: CommunityInfoRequest):
    """Create or update community info."""
    global _community
    with _lock:
        if _community is None:
            _community = {
                "name": data.name,
                "address": data.address,
                "phone": data.phone,
                "manager_name": data.manager_name,
                "updated_at": datetime.now().isoformat(),
            }
        else:
            for key, value in data.model_dump().items():
                _community[key] = value
            _community["updated_at"] = datetime.now().isoformat()
    _persist_community()
    logger.info(f"Community updated: {data.name}")
    return _community


@app.get("/community")
async def get_community():
    """Get community info."""
    with _lock:
        community = _community
    if community is None:
        raise HTTPException(
            status_code=404, detail="Community info not found"
        )
    logger.info("Get community requested")
    return community


# ── Run server ───────────────────────────────────────────────────────────────
def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Start uvicorn server."""
    config = Config(app, host=host, port=port, log_level="info")
    server = Server(config=config)
    logger.info(f"Starting server on {host}:{port}")
    server.run()


if __name__ == "__main__":
    run_server()
