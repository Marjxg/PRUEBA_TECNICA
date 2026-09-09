from pydantic import BaseModel

class TicketCreate(BaseModel):
    titulo: str
    descripcion: str | None = None

class TicketUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    estado: str | None = None

class TicketOut(BaseModel):
    id: int
    titulo: str
    descripcion: str | None
    estado: str