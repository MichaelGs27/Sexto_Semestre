from sqlalchemy import Column, Integer, String
from database import Base

class TipoId(Base):
    __tablename__ = "tiposid"
    cIdTipoId = Column(String(10), primary_key=True, index=True)
    cDescripcion = Column(String(100), nullable=False)

