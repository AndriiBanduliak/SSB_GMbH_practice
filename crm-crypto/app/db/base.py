"""
Base class for all database models
Import all models here for Alembic migrations
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic to detect them
# These imports must be after Base definition to avoid circular imports
def import_models():
    """Import models after Base is created"""
    from app.models.user import User  # noqa
    from app.models.client import Client, ClientAPIKey  # noqa
    from app.models.transaction import Transaction  # noqa
    from app.models.pnl import PnLRecord  # noqa
    from app.models.pipeline import Pipeline, PipelineStage  # noqa
    from app.models.task import Task  # noqa
    from app.models.audit import AuditLog  # noqa

