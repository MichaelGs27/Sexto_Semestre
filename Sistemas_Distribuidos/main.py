from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db, engine
from models import TipoId
from schemas import TipoIdCreate, TipoIdResponse
import models

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="API Tipos ID", version="1.0.0")

#CREAR un tipo ID
@app.post("/tiposid/", response_model=TipoIdResponse, status_code=status.HTTP_201_CREATED)
def create_tipo_id(tipo_id: TipoIdCreate, db: Session = Depends(get_db)):
    #Verificar si el tipo ID ya existe
    db_tipo_id = db.query(TipoId).filter(TipoId.cIdTipoId == tipo_id.cIdTipoId).first()
    if db_tipo_id:
        raise HTTPException(
            status_code = 400,
            detail = "El tipo ID ya existe"
        )
    #Crear un nuevo tipo ID
    db_tipo_id = TipoId(**tipo_id.dict())
    db.add(db_tipo_id)
    db.commit()
    db.refresh(db_tipo_id)
    return db_tipo_id
#OBTENER todos los tipos ID
@app.get("/tiposid/{cIdTipoId}", response_model=TipoIdResponse)
def obtener_tipo_id(cIdTipoId: str, db: Session = Depends(get_db)):
    db_tipo_id = db.query(TipoId).filter(TipoId.cIdTipoId == cIdTipoId).first()
    if db_tipo_id is None:
        raise HTTPException(status_code=404, detail="Tipo ID no encontrado")
    return db_tipo_id

#ACTUALIZAR un tipo ID
@app.put("/tiposid/{cIdTipoId}", response_model=TipoIdResponse)
def actualizar_tipo_id(cIdTipoId: str, tipo_id: TipoIdCreate, db: Session = Depends(get_db)):
    db_tipo_id = db.query(TipoId).filter(TipoId.cIdTipoId == cIdTipoId).first()
    if db_tipo_id is None:
        raise HTTPException(status_code=404, detail="Tipo ID no encontrado")
    db_tipo_id.cDescripcion = tipo_id.cDescripcion
    db.commit()
    db.refresh(db_tipo_id)
    return db_tipo_id

#ELIMINAR un tipo ID
@app.delete("/tiposid/{cIdTipoId}")
def eliminar_tipo_id(cIdTipoId: str, db: Session = Depends(get_db)):
    db_tipo_id = db.query(TipoId).filter(TipoId.cIdTipoId == cIdTipoId).first()
    if db_tipo_id is None:
        raise HTTPException(status_code=404, detail="Tipo ID no encontrado")
    db.delete(db_tipo_id)
    db.commit()
    return {"mensaje": "Tipo ID eliminado exitosamente"}


