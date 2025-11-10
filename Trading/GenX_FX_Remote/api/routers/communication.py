from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from datetime import datetime

from api.models.communication import Agent, Message, communication_db

router = APIRouter()

@router.post("/register", response_model=Agent)
async def register_agent(agent_data: Agent = Body(...)):
    """
    Registers a new agent with the communication hub.
    If an agent with the same email already exists, it updates the existing record.
    """
    # Check if an agent with this email already exists
    for agent_id, existing_agent in communication_db.agents.items():
        if existing_agent.email == agent_data.email:
            # Update existing agent's status and last_seen
            existing_agent.status = "online"
            existing_agent.last_seen = datetime.utcnow()
            return existing_agent

    # If no agent with that email, create a new one
    new_agent = Agent(name=agent_data.name, email=agent_data.email, status="online")
    communication_db.agents[new_agent.id] = new_agent
    return new_agent

@router.post("/messages")
async def send_message(message: Message):
    """
    Receives a message and adds it to the message queue.
    """
    if message.sender_id not in communication_db.agents:
        raise HTTPException(status_code=404, detail="Sender agent not registered.")

    communication_db.messages.append(message)
    return {"status": "message sent"}

@router.get("/messages/{agent_id}")
async def get_messages(agent_id: str):
    """
    Retrieves all messages for a specific agent.
    This includes broadcast messages and messages sent directly to the agent.
    """
    if agent_id not in communication_db.agents:
        raise HTTPException(status_code=404, detail="Agent not registered.")

    agent_messages = [
        msg for msg in communication_db.messages
        if msg.recipient_id == agent_id or msg.recipient_id == "broadcast"
    ]
    return agent_messages

@router.get("/status")
async def get_system_status():
    """
    Returns the current status of all registered agents.
    """
    return {"agents": communication_db.agents}

@router.post("/heartbeat/{agent_id}")
async def agent_heartbeat(agent_id: str):
    """
    Allows an agent to signal that it is still online.
    """
    if agent_id not in communication_db.agents:
        raise HTTPException(status_code=404, detail="Agent not registered.")

    agent = communication_db.agents[agent_id]
    agent.status = "online"
    agent.last_seen = datetime.utcnow()
    return {"status": f"Agent {agent_id} is online."}

@router.post("/state/{agent_id}")
async def update_agent_state(agent_id: str, state: Dict = Body(...)):
    """
    Allows an agent to update its shared state.
    """
    if agent_id not in communication_db.agents:
        raise HTTPException(status_code=404, detail="Agent not registered.")

    agent = communication_db.agents[agent_id]
    agent.state.update(state)
    agent.last_seen = datetime.utcnow() # Also update last_seen on state update

    return {"status": "state_updated", "agent_id": agent_id, "new_state": agent.state}