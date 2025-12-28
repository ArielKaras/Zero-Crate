from core.db import engine, Base
from core.db_models import Offer, UserOfferState, LedgerEvent

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
