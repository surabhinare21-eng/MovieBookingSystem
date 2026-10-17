from datetime import datetime, timedelta

from sqlalchemy import select, and_

from backend.app.models.shows import Show
from backend.app.models.movies import Movie
from backend.app.schemas.show import ShowCreate, ShowUpdate
from backend.app.services.seat_service import ensure_seats_for_screen

def get_show(db, show_id):
    return db.scalar(
        select(Show).where(Show.show_id == show_id)
    )


def get_all_show(db):
    """Retrieve all shows."""
    return list(
        db.scalars(select(Show)).all()
    )


def get_movie_duration(db, movie_id):
    """Fetch the selected movie and return its duration."""
    movie = db.scalar(
        select(Movie).where(Movie.movie_id == movie_id)
    )

    if movie is None:
        raise ValueError("Selected movie does not exist.")

    duration = movie.movie_duration

    if duration is None:
        raise ValueError("Movie duration is not configured.")

    duration_delta = timedelta(
        hours=duration.hour,
        minutes=duration.minute,
        seconds=duration.second,
    )

    if duration_delta.total_seconds() <= 0:
        raise ValueError("Movie duration must be greater than zero.")

    return duration_delta


def validate_start_time(start_time):
    """A show must be scheduled in the future."""
    if start_time <= datetime.now():
        raise ValueError(
            "Show start time must be in the future."
        )


def validate_screen_availability(
    db,
    screen_id,
    start_time,
    end_time,
    exclude_show_id=None,
):
    """
    Prevent overlapping active shows on the same screen.

    Two shows may be scheduled back-to-back.
    """
    query = select(Show).where(
        Show.screen_id == screen_id,
        Show.show_status.is_(True),
        Show.show_start_time < end_time,
        Show.show_end_time > start_time,
    )

    # Exclude the current show during an update.
    if exclude_show_id is not None:
        query = query.where(
            Show.show_id != exclude_show_id
        )

    conflicting_show = db.scalar(query)

    if conflicting_show is not None:
        raise ValueError(
            f"Screen {screen_id} is already occupied by "
            f"show {conflicting_show.show_id}, scheduled from "
            f"{conflicting_show.show_start_time} to "
            f"{conflicting_show.show_end_time}."
        )


def create_show(db, show_data: ShowCreate):
    """Create a show after validating its schedule."""
    start_time = show_data.show_start_time

    validate_start_time(start_time)

    duration = get_movie_duration(
        db,
        show_data.movie_id,
    )

    # Always calculate the end time on the backend.
    end_time = start_time + duration

    validate_screen_availability(
        db=db,
        screen_id=show_data.screen_id,
        start_time=start_time,
        end_time=end_time,
    )
    
        # Generate the screen's seats automatically if they do not exist.
    ensure_seats_for_screen(
        db=db,
        screen_id=show_data.screen_id,
    )
    

    show_values = show_data.model_dump(
        exclude={"show_end_time"}
    )
    show_values["show_end_time"] = end_time

    show = Show(**show_values)

    try:
        db.add(show)
        db.commit()
        db.refresh(show)
        return show
    except Exception:
        db.rollback()
        raise


def update_show(db, show_data: ShowUpdate, show_id):
    """Update a show while preserving scheduling rules."""
    show = get_show(db, show_id)

    if show is None:
        return None

    update_data = show_data.model_dump(
        exclude_unset=True,
        exclude={"show_end_time"},
    )

    start_time = update_data.get(
        "show_start_time",
        show.show_start_time,
    )

    screen_id = update_data.get(
        "screen_id",
        show.screen_id,
    )

    movie_id = update_data.get(
        "movie_id",
        show.movie_id,
    )

    validate_start_time(start_time)

    duration = get_movie_duration(db, movie_id)
    end_time = start_time + duration

    validate_screen_availability(
        db=db,
        screen_id=screen_id,
        start_time=start_time,
        end_time=end_time,
        exclude_show_id=show_id,
    )

    for field, value in update_data.items():
        setattr(show, field, value)

    # Recalculate end time whenever the schedule is updated.
    show.show_end_time = end_time

    try:
        db.commit()
        db.refresh(show)
        return show
    except Exception:
        db.rollback()
        raise


def update_show_status(db, show_id, show_status):
    """Activate or deactivate an existing show."""
    show = get_show(db, show_id)

    if show is None:
        return None

    # Recheck conflicts when reactivating a show.
    if show_status:
        validate_screen_availability(
            db=db,
            screen_id=show.screen_id,
            start_time=show.show_start_time,
            end_time=show.show_end_time,
            exclude_show_id=show_id,
        )

    show.show_status = show_status

    try:
        db.commit()
        db.refresh(show)
        return show
    except Exception:
        db.rollback()
        raise