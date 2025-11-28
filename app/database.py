from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLITE_DATABASE_URL = "sqlite:///./leads.db"
engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы успешно созданы")
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")