from app.core.base import Base
from app.core.database import engine
from app.models import Booking


Base.metadata.create_all(bind=engine)

print("Booking service database tables created successfully.")