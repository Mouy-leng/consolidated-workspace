from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
import uuid

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str = "offline"
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    email: str # Added email to link to the user account
    state: Dict[str, Any] = {} # Added state for more detailed status

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str  # Can be a specific agent ID or "broadcast"
    event_type: str  # e.g., "task_update", "deployment_status"
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CommunicationState(BaseModel):
    agents: Dict[str, Agent] = {}
    messages: List[Message] = []

# In-memory store for our communication hub
# A more robust solution would use Redis or a database.
communication_db = CommunicationState()