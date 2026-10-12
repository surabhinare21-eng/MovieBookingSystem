from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.show import (
    ShowCreate,
    ShowUpdate,
    ShowOut,
    ShowStatus,
)
from backend.app.services import show_service

router = APIRouter(prefix="/shows", tags=["Shows"])

@router.post(
    "/",
    response_model=ShowOut,
    status_code=status.HTTP_201_CREATED
)
def create_show(show:ShowCreate, db:Session = Depends(get_db)):
    return show_service.create_show(db, show)


@router.get("/{show_id}", response_model=ShowOut)
def get_show(show_id, db:Session=Depends(get_db)):
    result = show_service.get_show(db, show_id)
    if result is None:
        raise HTTPException(status_code=404, detail="show not found ...")
    return result

@router.get("/", response_model=list[ShowOut])
def get_all_shows(db: Session=Depends(get_db)):
    
    return show_service.get_all_show(db)


def update_show(show:ShowUpdate, show_id, db: Session=Depends(get_db) ):
    result= show_service.update_show(db, show_id, show)
    
    if result is None:
        raise HTTPException(status_code=404, detail="show not found to update")
        
    
    return result


@router.patch(
    "/{show_id}/status",
    response_model=ShowOut
)

def update_show_status(show_id, show:ShowStatus, db:Session = Depends(get_db)):
    result =show_service.update_show_status(db, show_id, show)
    if result is None:
        raise HTTPException(status_code=404,detail="Show not found")
    
    return result

