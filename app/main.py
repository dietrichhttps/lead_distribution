from app.api.api import app
import uvicorn

from app.database import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)