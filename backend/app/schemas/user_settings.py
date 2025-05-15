from pydantic import BaseModel
from typing import Dict, Optional


class UserSettings(BaseModel):
    setting_id: str
    user_id: str
    notification_preferences: Dict[str, bool]
    ui_preferences: Dict[str, str]
    time_zone: Optional[str] = None
    language_preference: Optional[str] = "en"