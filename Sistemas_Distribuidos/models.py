from sqlalchemy import column, Integer, String
from database import Base

class TipoId(Base):
    __tablename__ = "TiposId"
    cIdTipoId = column(Integer, primary_key=True, index=True)
    cDescripcion = column(String(45), nullable=False)