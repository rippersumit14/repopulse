from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all RepoPulse SQLAlchemy models.

    Every database model will inherit from this class so SQLAlchemy
    can track the table definitions and use them with Alembic
    """
    pass
