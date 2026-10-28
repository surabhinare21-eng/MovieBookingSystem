"""Demo seed for MovieBookingSystem.

Run from the project root with: python seed.py

Creates/reuses 10 Indian cities, 20 real movies, 10 theatres (one per city),
10 theatre-admin accounts, 3 screens per theatre, seats, and a week of future
shows. Poster URLs are fetched from Wikipedia at runtime; a visible placeholder
is used only if a real reachable image URL cannot be found. Safe to rerun for
existing seeded rows; it does not delete unrelated records.

All seeded theatre admins use the initial demo password: Skcp@2026
"""
from datetime import date, datetime, time, timedelta
from urllib.parse import quote

import requests
from sqlalchemy import func, select

from database import engine
from backend.app.core.security import hash_password
from backend.app.db.base import Base
from backend.app.db.session import SessionLocal
from backend.app.models.user import Role, User
from backend.app.models.city import City
from backend.app.models.theatre import Theatre
from backend.app.models.screens import Screen
from backend.app.models.shows import Show
from backend.app.models.movies import Movie
from backend.app.models.booking import Booking  # noqa: F401
from backend.app.models.payment import Payment  # noqa: F401
from backend.app.models.seat import Seat, SeatLock  # noqa: F401
from backend.app.models.booking_seat import BookingSeat  # noqa: F401
from backend.app.models.show_enums import ShowFormat, ShowLanguages
from backend.app.services.seat_service import ensure_seats_for_screen
from backend.app.services.show_service import validate_screen_availability

H, M = ShowLanguages.HINDI, ShowLanguages.MARATHI

# Approximate city-centre coordinates required by the City model.
CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Nagpur": (21.1458, 79.0882),
}

ADMIN_PASSWORD = "Skcp@2026"
DAYS = 7
SLOTS = [time(10, 0), time(14, 0), time(18, 30), time(22, 0)]
SCREENS = [("Screen 1", "small"), ("Screen 2", "medium"), ("Screen 3", "large")]

# city, theatre name, address, admin (username, email) -> one theatre per city
THEATRES = [
    ("Mumbai",    "PVR Andheri",              "Andheri West, Mumbai",          ("Sharvari",  "sharvari@gmail.com")),
    ("Delhi",     "INOX Connaught Place",     "Connaught Place, New Delhi",    ("Vibhor",    "vibhor@gmail.com")),
    ("Bengaluru", "Cinepolis Koramangala",    "Koramangala, Bengaluru",        ("Aditya",    "aditya@gmail.com")),
    ("Hyderabad", "PVR Banjara Hills",        "Banjara Hills, Hyderabad",      ("Neha",      "neha@gmail.com")),
    ("Ahmedabad", "INOX Satellite",           "Satellite, Ahmedabad",          ("Rohan",     "rohan@gmail.com")),
    ("Chennai",   "Carnival T. Nagar",        "T. Nagar, Chennai",             ("Priya",     "priya@gmail.com")),
    ("Kolkata",   "INOX Salt Lake",           "Salt Lake, Kolkata",            ("Karan",     "karan@gmail.com")),
    ("Pune",      "PVR Kothrud",              "Kothrud, Pune",                 ("Ananya",    "ananya@gmail.com")),
    ("Jaipur",    "Cinepolis Malviya Nagar",  "Malviya Nagar, Jaipur",         ("Siddharth", "siddharth@gmail.com")),
    ("Nagpur",    "Carnival Dharampeth",      "Dharampeth, Nagpur",            ("Isha",      "isha@gmail.com")),
]

# (title, wikipedia page, description, language, genre, rating 0-10, h, m)
MOVIES = [
    ("3 Idiots", "3 Idiots", "Two friends look back on their engineering college days and search for the brilliant, rule-breaking friend who changed how they saw success.", H, "Comedy-Drama", 9, 2, 50),
    ("Dangal", "Dangal (film)", "A former wrestler trains his two daughters to become champions in a society that says girls cannot wrestle.", H, "Sports Biography", 9, 2, 41),
    ("Lagaan", "Lagaan", "Villagers accept a British officer's cricket challenge to escape a crushing tax during a drought.", H, "Sports Drama", 8, 3, 44),
    ("Sholay", "Sholay", "Two small-time crooks are hired by a former police chief to capture a feared bandit terrorising a village.", H, "Action Adventure", 8, 3, 24),
    ("Dilwale Dulhania Le Jayenge", "Dilwale Dulhania Le Jayenge", "Two young Indians fall in love on a Europe trip, then must win over a strict father back home.", H, "Romance", 8, 3, 9),
    ("Zindagi Na Milegi Dobara", "Zindagi Na Milegi Dobara", "Three friends take a bachelor road trip across Spain and rediscover what really matters to them.", H, "Adventure Comedy", 8, 2, 35),
    ("Andhadhun", "Andhadhun", "A pianist pretending to be blind becomes tangled in a murder, and every lie makes things worse.", H, "Thriller", 8, 2, 19),
    ("Taare Zameen Par", "Taare Zameen Par", "A teacher helps an eight-year-old who struggles at school discover the talent hidden behind his difficulties.", H, "Drama", 9, 2, 45),
    ("Sairat", "Sairat", "A boy from a poor family and a landlord's daughter fall in love and run away from their village.", M, "Romance Drama", 8, 2, 54),
    ("Court", "Court (2014 film)", "A folk singer is put on trial in a slow Mumbai court, exposing the flaws of the legal system.", M, "Courtroom Drama", 7, 1, 56),
    ("Bajrangi Bhaijaan", "Bajrangi Bhaijaan", "A devoted Hanuman follower helps a mute Pakistani girl who is lost in India find her way home across the border.", H, "Drama", 8, 2, 43),
    ("PK", "PK (film)", "An alien stranded on Earth asks awkward questions about religion and belief while searching for his lost device.", H, "Comedy-Drama", 8, 2, 33),
    ("Queen", "Queen (2014 film)", "After her fiance calls off their wedding, a shy Delhi girl goes on her honeymoon alone and discovers herself.", H, "Comedy-Drama", 8, 2, 26),
    ("Gully Boy", "Gully Boy", "A young man from a Mumbai slum finds his voice as a rapper and fights to turn his poetry into a career.", H, "Musical Drama", 8, 2, 33),
    ("Barfi!", "Barfi!", "A charming deaf-mute man in 1970s Darjeeling wins hearts in a love story told through humour and silent moments.", H, "Romantic Comedy", 8, 2, 31),
    ("Drishyam", "Drishyam (2015 film)", "A cable operator protects his family with a clever story after a crime threatens them, challenging a determined police officer.", H, "Thriller", 8, 2, 43),
    ("Swades", "Swades", "An NRI NASA engineer returns to a small Indian village and slowly decides to help bring it electricity.", H, "Drama", 8, 3, 9),
    ("Rang De Basanti", "Rang De Basanti", "College friends playing freedom fighters in a documentary are pushed to act when tragedy exposes corruption.", H, "Drama", 8, 2, 47),
    ("Chak De! India", "Chak De! India", "A disgraced hockey star coaches the Indian women's team, uniting players from different states for the World Cup.", H, "Sports Drama", 8, 2, 33),
    ("Dil Chahta Hai", "Dil Chahta Hai", "Three close friends drift apart and find love as they grow up, with Goa, Sydney and Mumbai shaping their lives.", H, "Comedy-Drama", 8, 3, 3),
]

UA = {"User-Agent": "MovieBookingDemoSeed/1.0 (student project; poster lookup)"}
WIKI_API = "https://en.wikipedia.org/w/api.php"


def placeholder(title: str) -> str:
    return f"https://placehold.co/300x450/png?text={quote(title)}"


def _thumb_from(params: dict) -> str | None:
    base = {
        "action": "query", "format": "json", "redirects": 1,
        "prop": "pageimages", "piprop": "thumbnail",
        "pithumbsize": 500, "pilicense": "any",   # 'any' => film posters too
    }
    r = requests.get(WIKI_API, params={**base, **params}, headers=UA, timeout=12)
    r.raise_for_status()
    for page in r.json().get("query", {}).get("pages", {}).values():
        src = page.get("thumbnail", {}).get("source")
        if src:
            return src
    return None


def _image_is_reachable(url: str) -> bool:
    try:
        r = requests.get(url, headers=UA, timeout=12, stream=True)
        ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image")
        r.close()
        return ok and len(url) <= 500
    except requests.RequestException:
        return False


def find_poster(title: str, wiki_page: str) -> str | None:
    """Return a working poster URL from Wikipedia, or None."""
    try:
        for params in (
            {"titles": wiki_page},
            {"generator": "search", "gsrsearch": f"{title} Indian film", "gsrlimit": 1},
        ):
            url = _thumb_from(params)
            if url and _image_is_reachable(url):
                return url
    except (requests.RequestException, ValueError):
        pass
    return None


def seed_cities_theatres_admins(db):
    created = {"cities": 0, "theatres": 0, "admins": 0}
    theatre_rows = []  # (Theatre, admin_email)
    for i, (city_name, t_name, address, (username, email)) in enumerate(THEATRES):
        city = db.scalar(select(City).where(City.name == city_name))
        if city is None:
            latitude, longitude = CITY_COORDINATES[city_name]
            city = City(name=city_name, latitude=latitude, longitude=longitude, is_active=True)
            db.add(city)
            db.flush()
            created["cities"] += 1

        theatre = db.scalar(select(Theatre).where(
            Theatre.name == t_name, Theatre.city_id == city.city_id))
        if theatre is None:
            theatre = Theatre(
                name=t_name, city_id=city.city_id,
                address=f"{10 + i * 7} Main Road, {address}",
                contact_info=f"+91 90000 {city.city_id:02d}{i:03d}",
                is_active=True,
            )
            db.add(theatre)
            db.flush()
            created["theatres"] += 1

        if db.scalar(select(User).where(User.user_email == email)) is None:
            db.add(User(
                username=username, user_email=email,
                phone_no=f"+91 98765 {i + 1:05d}",
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=Role.ADMIN.value, theatre_id=theatre.theatre_id,
                is_active=True,
            ))
            created["admins"] += 1
        theatre_rows.append((theatre, email))
    db.commit()
    return created, theatre_rows


def seed_movies(db) -> tuple[int, int, int]:
    added = upgraded = placeholders = 0
    for title, wiki, desc, lang, genre, rating, h, m in MOVIES:
        assert len(desc) <= 255 and 0 <= rating <= 10
        movie = db.scalar(select(Movie).where(Movie.movie_title == title))
        if movie is None:
            poster = find_poster(title, wiki) or placeholder(title)
            db.add(Movie(
                movie_title=title, movie_description=desc, movie_status="ACTIVE",
                movie_language=lang, movie_poster_url=poster, movie_genre=genre,
                movie_rating=rating, movie_duration=time(h, m, 0),
            ))
            added += 1
            placeholders += poster.startswith("https://placehold.co")
        elif movie.movie_poster_url.startswith("https://placehold.co"):
            real = find_poster(title, wiki)
            if real:
                movie.movie_poster_url = real
                upgraded += 1
            else:
                placeholders += 1
        print(f"  movie: {title}")
    db.commit()
    return added, upgraded, placeholders


def seed_screens(db, theatre: Theatre) -> list[Screen]:
    existing = {s.screen_name: s for s in db.scalars(
        select(Screen).where(Screen.theatre_id == theatre.theatre_id))}
    for name, layout in SCREENS:
        if name not in existing:
            db.add(Screen(theatre_id=theatre.theatre_id, screen_name=name,
                          seat_layout_name=layout, screen_is_active=True))
    db.commit()
    return list(db.scalars(
        select(Screen).where(Screen.theatre_id == theatre.theatre_id,
                             Screen.screen_is_active.is_(True))
        .order_by(Screen.screen_id)))


def duration_of(movie: Movie) -> timedelta:
    d = movie.movie_duration
    return timedelta(hours=d.hour, minutes=d.minute, seconds=d.second)


def seed_shows(db, theatre_index: int, theatre: Theatre, movies: list[Movie]) -> int:
    first_day = date.today() + timedelta(days=1)
    created = 0
    for s_index, screen in enumerate(seed_screens(db, theatre)):
        ensure_seats_for_screen(db=db, screen_id=screen.screen_id)
        db.commit()
        for day in range(DAYS):
            this_day = first_day + timedelta(days=day)
            for slot_no, slot in enumerate(SLOTS):
                start = datetime.combine(this_day, slot)
                if slot_no < len(SLOTS) - 1:
                    next_start = datetime.combine(this_day, SLOTS[slot_no + 1])
                else:
                    next_start = datetime.combine(this_day + timedelta(days=1), SLOTS[0])

                base = theatre_index * 3 + s_index * 5 + day * 2 + slot_no
                chosen = None
                for offset in range(len(movies)):          # first movie that fits the gap
                    candidate = movies[(base + offset) % len(movies)]
                    if start + duration_of(candidate) <= next_start:
                        chosen = candidate
                        break
                if chosen is None:
                    continue
                end = start + duration_of(chosen)
                try:
                    validate_screen_availability(
                        db=db, screen_id=screen.screen_id,
                        start_time=start, end_time=end)
                except ValueError:
                    continue  # already scheduled (re-run) or clash
                fmt = ShowFormat.D4X if s_index == 2 and (day + slot_no) % 4 == 0 else ShowFormat.D2
                db.add(Show(
                    show_start_time=start, show_end_time=end, show_status=True,
                    show_language=chosen.movie_language, show_format=fmt,
                    screen_id=screen.screen_id, movie_id=chosen.movie_id))
                db.flush()  # autoflush is off; make it visible to the next clash check
                created += 1
        db.commit()
    return created


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Cities, theatres and theatre admins...")
        created, theatre_rows = seed_cities_theatres_admins(db)

        print("Movies (looking up poster URLs on Wikipedia)...")
        added, upgraded, placeholders = seed_movies(db)

        movies = list(db.scalars(
            select(Movie).where(Movie.movie_status == "ACTIVE").order_by(Movie.movie_id)))

        print("Screens and shows...")
        total_shows = 0
        for t_index, (theatre, _email) in enumerate(theatre_rows):
            n = seed_shows(db, t_index, theatre, movies)
            total_shows += n
            upcoming = db.scalar(
                select(func.count(Show.show_id))
                .join(Screen, Show.screen_id == Screen.screen_id)
                .where(Screen.theatre_id == theatre.theatre_id,
                       Show.show_status.is_(True),
                       Show.show_start_time > datetime.now()))
            print(f"  {theatre.name}: +{n} new, {upcoming} upcoming")

        print("\n=== Done ===")
        print(f"New: {created['cities']} cities, {created['theatres']} theatres, "
              f"{created['admins']} theatre admins, {added} movies, {total_shows} shows.")
        if upgraded:
            print(f"Posters upgraded from placeholder to real: {upgraded}")
        if placeholders:
            print(f"WARNING: {placeholders} movie(s) still use a placeholder poster "
                  f"(no internet or Wikipedia lookup failed). Run this script again later.")
        print(f"\nTheatre admin logins (password for all: {ADMIN_PASSWORD})")
        for (theatre, email), (city, *_rest) in zip(theatre_rows, THEATRES):
            print(f"  {email:<26} -> {theatre.name}, {city}")
    finally:
        db.close()


if __name__ == "__main__":
    main()