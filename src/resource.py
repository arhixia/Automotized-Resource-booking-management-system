from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import get_db
from src.models import Resource

resource_router = APIRouter(
    prefix="/resources",
    tags=["resources"]
)

class ResourceCreate(BaseModel):
    name: str
    type: str
    capacity: int
    price: int

@resource_router.get("/")
def get_resources(db: Session = Depends(get_db)):
    resources = db.query(Resource).all()
    return resources

@resource_router.post("/", status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.name == resource.name).first()
    if db_resource:
        raise HTTPException(status_code=400, detail="Resource already exists")

    new_resource = Resource(**resource.dict())
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

@resource_router.put("/{resource_id}")
def update_resource(resource_id: int, resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    for key, value in resource.dict().items():
        setattr(db_resource, key, value)

    db.commit()
    db.refresh(db_resource)
    return db_resource

@resource_router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    db.delete(db_resource)
    db.commit()
    return {"detail": "Resource deleted successfully"}
