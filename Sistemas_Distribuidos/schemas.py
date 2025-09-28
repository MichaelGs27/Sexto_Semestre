from pydantic import BaseModel
from typing import Optional

class TipoIdBase(BaseModel):
    cIdTipoId: str
    cDescripcion: str

class TipoIdCreate(TipoIdBase):
    pass

class TipoIdResponse(TipoIdBase):

    class Config:
        from_attributes = True