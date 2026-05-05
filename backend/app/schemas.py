from pydantic import BaseModel

class Signal(BaseModel):
    component_id: str
    severity: str


class RCARequest(BaseModel):
    root_cause: str
    fix: str
