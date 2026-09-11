from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://marine:marine@localhost:5432/marine_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT PostGIS_Full_Version()"))
        return result.scalar()


if __name__ == "__main__":
    print(test_connection())
