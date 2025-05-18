from typing import Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID
import secrets

class StateStorage:
    def __init__(self):
        self._storage: Dict[str, datetime] = {}
        self._expiry_time = timedelta(minutes=5)  # States expire after 5 minutes

    def generate_state(self) -> str:
        """Generate a new state token."""
        state = str(UUID(bytes=secrets.token_bytes(16)))
        self._storage[state] = datetime.utcnow()
        return state

    def validate_state(self, state: str) -> bool:
        """Validate a state token."""
        if state not in self._storage:
            return False
        
        # Check if state has expired
        created_time = self._storage[state]
        if datetime.utcnow() - created_time > self._expiry_time:
            del self._storage[state]
            return False
        
        # State is valid, remove it to prevent reuse
        del self._storage[state]
        return True
