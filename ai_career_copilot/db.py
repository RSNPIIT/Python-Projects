from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base , sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping = True,
    connect_args = {
        'ssl' :{
            "ssl" : True

        }
    } 
)

SessionLocal = sessionmaker(bind = engine)
Base = declarative_base()