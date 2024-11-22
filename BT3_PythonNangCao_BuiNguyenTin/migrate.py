from sqlalchemy import create_engine
from config import DATABASE_URL
from models import Base

def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
