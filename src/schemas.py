from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LeadType(str, Enum):
    LOCATION = "location"
    ACHAT = "achat"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Lead(BaseModel):
    """Données extraites du message du prospect (tout est optionnel :
    le LLM met null quand l'info est absente)."""
    type: Optional[LeadType] = None
    city: Optional[str] = None
    budget: Optional[float] = Field(default=None, ge=0)
    property_type: Optional[str] = None      # ex. "T2", "studio", "maison"
    bedrooms: Optional[int] = Field(default=None, ge=0, le=20)
    move_in_date: Optional[str] = None       # texte libre : "novembre", "ASAP"

    @field_validator("city", "property_type", "move_in_date", mode="before")
    @classmethod
    def clean_str(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("budget", mode="before")
    @classmethod
    def clean_budget(cls, v):
        # le LLM renvoie parfois "1200€" ou "1 200"
        if isinstance(v, str):
            digits = "".join(c for c in v if c.isdigit() or c == ".")
            return float(digits) if digits else None
        return v


class QualifiedLead(BaseModel):
    """Lead + résultat du scoring, c'est ce qui part vers n8n."""
    lead: Lead
    score: int = Field(ge=0, le=100)
    priority: Priority
    raw_message: str