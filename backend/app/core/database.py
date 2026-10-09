"""
Example database.py — the shared connection setup every module relies on.
Lives in app/core/database.py. Written once, imported everywhere.
"""


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from app.core.config import settings

# 1. Connection string comes from env vars (never hardcoded):
#    mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/mtb"
# 2. Engine: manages a pool of real connections to MySQL.
#    pool_pre_ping checks a connection is alive before using it,
#    which avoids "MySQL server has gone away" errors on idle connections.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,

)

# 3. SessionLocal: a factory for creating new sessions.
#    autocommit=False means YOU control when changes are saved (session.commit()).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base: every model class (Movie, Show, Booking...) inherits from this,
#    so SQLAlchemy knows to map them to real tables.
Base = declarative_base()


# 5. get_db(): FastAPI dependency. Every route that needs the DB
#    adds `db: Session = Depends(get_db)` as a parameter.
def get_db():
    db = SessionLocal()
    try:
        yield db          # hands the session to the route
    finally:
        db.close()         # always closes it, even if the route raised an error
        
 