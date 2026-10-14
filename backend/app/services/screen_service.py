
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.screens import Screen
from backend.app.schemas.screen import ScreenCreate, ScreenUpdate


def create_screen(
    db: Session,
    theatre_id: int,
    payload: ScreenCreate,
) -> Screen:
    values = payload.model_dump()

    screen = Screen(
        theatre_id=theatre_id,
        screen_name=values["screen_name"].strip(),
        seat_layout_name=values["seat_layout_name"],
        screen_is_active=values.get("screen_is_active", False),
    )

    db.add(screen)
    db.commit()
    db.refresh(screen)

    return screen


def get_screens_by_theatre(
    db: Session,
    theatre_id: int,
) -> list[Screen]:
    return list(
        db.scalars(
            select(Screen)
            .where(Screen.theatre_id == theatre_id)
            .order_by(Screen.screen_id)
        )
    )


def get_screen_by_id(
    db: Session,
    screen_id: int,
    theatre_id: int,
) -> Screen | None:
    return db.scalar(
        select(Screen).where(
            Screen.screen_id == screen_id,
            Screen.theatre_id == theatre_id,
        )
    )


def update_screen(
    db: Session,
    screen: Screen,
    payload: ScreenUpdate,
) -> Screen:
    changes = payload.model_dump(exclude_unset=True)

    if changes.get("screen_name") is not None:
        changes["screen_name"] = changes["screen_name"].strip()

    for field, value in changes.items():
        setattr(screen, field, value)

    db.commit()
    db.refresh(screen)

    return screen


def delete_screen(db: Session, screen: Screen) -> None:
    db.delete(screen)
    db.commit()
