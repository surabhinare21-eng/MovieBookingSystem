
from pydantic import BaseModel
from sqlalchemy.orm import session
from sqlalchemy import select
from backend.app.models.shows import Show
from backend.app.schemas.show import ShowCreate, ShowUpdate
def create_show(db, show_data: ShowCreate):
    """Creating a new show by the admin"""
    if show_data.show_end_time <= show_data.show_start_time :
        raise ValueError("show end time should be after show start time")
    
    show = Show(**show_data.model_dump())
    
    db.add(show)
    db.commit()
    db.refresh(show)
    
    return show

def get_show(db, show_id):
    return db.scalar(select(Show).where(Show.show_id==show_id))

def get_all_show(db):
    """Retrieve all shows"""
    return list(db.scalars(select(Show)).all())

def update_show(db, show_data, show_id):
    """Update the shows data for the show id"""
    
    show = get_show(db, show_id)
    if show is None:
        return None
    
    update_data = show_data.model_dump(exclude_unset=True)
    start_time = update_data.get("show_start_time", show.show_start_time)
    end_time = update_data.get("show_end_time", show.show_end_time)
    
    if start_time is not None and end_time is not None:
        if end_time<=start_time:
            raise ValueError("show end time must be after the end time")
        
    for field, value in update_data.items():
        setattr(show, field, value)
        
    db.commit()
    db.refresh(show)
    
    return show

def update_show_status(
    db,
    show_id,
    show_status,
):
    """Updating the status of an existing show."""

    show = get_show(db, show_id)

    if show is None:
        return None

    show.show_status = show_status

    db.commit()
    db.refresh(show)

    return show
    
    
    