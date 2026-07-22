from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.council_configuration import ConfigurationSource

class CouncilConfigurationBase(BaseModel):
    logical_weight: int
    practical_weight: int
    analytical_weight: int
    skeptical_weight: int
    ethics_weight: int
    
    logical_enabled: bool
    practical_enabled: bool
    analytical_enabled: bool
    skeptical_enabled: bool
    ethics_enabled: bool

class CouncilConfigurationRead(CouncilConfigurationBase):
    id: UUID
    message_id: UUID
    source: ConfigurationSource
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
