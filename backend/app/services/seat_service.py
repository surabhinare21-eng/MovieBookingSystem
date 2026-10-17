
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.screens import Screen
from backend.app.models.shows import Show
from backend.app.models.seat import Seat, SeatLock
from datetime import datetime, timedelta
from sqlalchemy import select, update


# Layout name: (number of rows, number of columns)


SEAT_LAYOUTS = {
    "compact": (5, 10),
    "small": (10, 10),
    "medium": (15, 10),
    "large": (25, 10),
}


def get_layout_dimensions(seat_layout_name: str) -> tuple[int, int]:
    """Return the row and column count for a configured layout."""

    layout_name = seat_layout_name.strip().lower()

    if layout_name not in SEAT_LAYOUTS:
        raise ValueError(
            f"Unsupported seat layout: {seat_layout_name}"
        )

    return SEAT_LAYOUTS[layout_name]


def generate_seats_for_screen(
    db: Session,
    screen_id: int,
) -> list[Seat] | None:
    """Generate physical seats for a screen once."""

    screen = db.get(Screen, screen_id)

    if screen is None:
        return None

    existing_seats = db.scalars(
        select(Seat).where(Seat.screen_id == screen_id)
    ).all()

    # Do not generate duplicate seats for an existing layout.
    if existing_seats:
        return list(existing_seats)

    rows, cols = get_layout_dimensions(screen.seat_layout_name)

    seats = []

    for row_index in range(rows):
        row_label = chr(ord("A") + row_index)

        # The top 20% of rows are Platinum; the rest are Gold.
        platinum_rows = max(1, rows // 5)
        seat_type = (
            "PLATINUM"
            if row_index >= rows - platinum_rows
            else "GOLD"
        )

        for col_index in range(1, cols + 1):
            seat = Seat(
                screen_id=screen_id,
                row_no=row_index + 1,
                col_no=col_index,
                seat_label=f"{row_label}{col_index:02d}",
                seat_type=seat_type,
            )
            seats.append(seat)

    try:
        db.add_all(seats)
        db.commit()

        for seat in seats:
            db.refresh(seat)

        return seats

    except Exception:
        db.rollback()
        raise



def get_seats_for_show(
    db: Session,
    show_id: int,
) -> list[dict] | None:
    """Return seat availability for a particular show."""

    show = db.get(Show, show_id)

    if show is None:
        return None

    seats = list(
        db.scalars(
            select(Seat)
            .where(Seat.screen_id == show.screen_id)
            .order_by(Seat.row_no, Seat.col_no)
        ).all()
    )

    now = datetime.now()

    locks = db.scalars(
        select(SeatLock).where(
            SeatLock.show_id == show_id,
            SeatLock.lock_status.in_(["ACTIVE", "CONFIRMED"]),
        )
    ).all()

    status_by_seat = {}
    expired_locks = []

    for lock in locks:
        if lock.lock_status == "CONFIRMED":
            # Only a genuinely paid/confirmed booking belongs here.
            status_by_seat[lock.seat_id] = "BOOKED"

        elif lock.expires_at <= now:
            lock.lock_status = "EXPIRED"
            expired_locks.append(lock)

        else:
            # Temporary hold: unavailable, but not booked.
            status_by_seat[lock.seat_id] = "HOLD"

    if expired_locks:
        db.commit()

    result = []

    for seat in seats:
        result.append({
            "seat_id": seat.seat_id,
            "screen_id": seat.screen_id,
            "row_no": seat.row_no,
            "col_no": seat.col_no,
            "seat_label": seat.seat_label,
            "seat_type": seat.seat_type,
            "seat_status": status_by_seat.get(
                seat.seat_id, "AVAILABLE"
            ),
        })

    return result



def lock_seats_for_show(
    db: Session,
    show_id: int,
    seat_ids: list[int],
    user_id: int,
) -> list[SeatLock]:
    """
    Atomically hold multiple seats for one customer for five minutes.

    All requested seats are locked together, or none are locked.
    """

    if not seat_ids:
        raise ValueError("Please select at least one seat.")

    if len(seat_ids) > 10:
        raise ValueError("You can select a maximum of 10 seats.")

    if len(set(seat_ids)) != len(seat_ids):
        raise ValueError("Duplicate seat IDs are not allowed.")

    try:
        # 1. Verify that the show exists.
        show = db.get(Show, show_id)

        if show is None:
            raise ValueError("Show not found.")

        # 2. Lock physical seat rows in a consistent order.
        # This serializes competing requests for the same seats in MySQL.
        seats = db.scalars(
            select(Seat)
            .where(
                Seat.seat_id.in_(seat_ids),
                Seat.screen_id == show.screen_id,
            )
            .order_by(Seat.seat_id)
            .with_for_update()
        ).all()

        if len(seats) != len(seat_ids):
            raise ValueError(
                "One or more seats do not belong to this show's screen."
            )

        # 3. Check existing holds/bookings for this show.
        now = datetime.now()

        existing_locks = db.scalars(
            select(SeatLock)
            .where(
                SeatLock.show_id == show_id,
                SeatLock.seat_id.in_(seat_ids),
                SeatLock.lock_status.in_(["ACTIVE", "CONFIRMED"]),
            )
            .with_for_update()
        ).all()

        unavailable_seats = []

        for lock in existing_locks:
            if lock.lock_status == "CONFIRMED":
                unavailable_seats.append(lock.seat_id)

            elif lock.expires_at > now:
                unavailable_seats.append(lock.seat_id)

            else:
                # An active hold has expired.
                lock.lock_status = "EXPIRED"

        if unavailable_seats:
            labels = [
                seat.seat_label
                for seat in seats
                if seat.seat_id in unavailable_seats
            ]

            raise ValueError(
                "These seats are already booked or held: "
                + ", ".join(labels)
            )

        # 4. Create a five-minute hold for every requested seat.
        expires_at = now + timedelta(minutes=5)

        new_locks = []

        for seat in seats:
            lock = SeatLock(
                show_id=show_id,
                seat_id=seat.seat_id,
                user_id=user_id,
                screen_id=show.screen_id,
                locked_at=now,
                expires_at=expires_at,
                lock_status="ACTIVE",
            )

            db.add(lock)
            new_locks.append(lock)

        # 5. Commit every hold together.
        db.commit()

        for lock in new_locks:
            db.refresh(lock)

        return new_locks

    except Exception:
        db.rollback()
        raise


def release_seats_for_show(
    db: Session,
    show_id: int,
    seat_ids: list[int],
    user_id: int,
) -> int:
    """Release active seat holds owned by this customer."""

    if not seat_ids:
        raise ValueError("Please select at least one seat.")

    if len(set(seat_ids)) != len(seat_ids):
        raise ValueError("Duplicate seat IDs are not allowed.")

    try:
        now = datetime.now()

        locks = db.scalars(
            select(SeatLock)
            .where(
                SeatLock.show_id == show_id,
                SeatLock.seat_id.in_(seat_ids),
                SeatLock.user_id == user_id,
                SeatLock.lock_status == "ACTIVE",
            )
            .with_for_update()
        ).all()

        released_count = 0

        for lock in locks:
            if lock.expires_at > now:
                lock.lock_status = "RELEASED"
                released_count += 1
            else:
                lock.lock_status = "EXPIRED"

        db.commit()
        return released_count

    except Exception:
        db.rollback()
        raise


def ensure_seats_for_screen(db: Session, screen_id: int) -> list[Seat]:
    """Ensure that a screen has its physical seats created."""

    screen = db.get(Screen, screen_id)

    if screen is None:
        raise ValueError("Screen not found.")

    existing_seats = list(
        db.scalars(
            select(Seat)
            .where(Seat.screen_id == screen_id)
            .order_by(Seat.row_no, Seat.col_no)
        ).all()
    )

    if existing_seats:
        return existing_seats

    rows, cols = get_layout_dimensions(screen.seat_layout_name)
    seats = []

    platinum_rows = max(1, rows // 5)

    for row_index in range(rows):
        row_label = chr(ord("A") + row_index)

        seat_type = (
            "PLATINUM"
            if row_index >= rows - platinum_rows
            else "GOLD"
        )

        for col_index in range(1, cols + 1):
            seats.append(
                Seat(
                    screen_id=screen_id,
                    row_no=row_index + 1,
                    col_no=col_index,
                    seat_label=f"{row_label}{col_index:02d}",
                    seat_type=seat_type,
                )
            )

    db.add_all(seats)
    db.flush()

    return seats