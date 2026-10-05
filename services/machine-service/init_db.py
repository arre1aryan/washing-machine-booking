from app.core.base import Base
from app.core.database import engine
from app.models import Machine, Slot


Base.metadata.create_all(bind=engine)

print("Machine service database tables created successfully.")