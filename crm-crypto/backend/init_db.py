"""
Initialize database with first superuser
Run this script after applying migrations
"""
import asyncio
import sys
from sqlalchemy import select

# Import Base first to avoid circular imports
from app.db.base import Base

# Import engine before session
from app.db.session import engine, AsyncSessionLocal

# Import models after Base
from app.models.user import User
from app.models.pipeline import Pipeline, PipelineStage
from app.models.client import Client, ClientAPIKey
from app.models.transaction import Transaction
from app.models.pnl import PnLRecord
from app.models.task import Task
from app.models.audit import AuditLog

from app.core.security import get_password_hash
from app.core.config import settings


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {str(e)}")
        raise


async def create_superuser():
    """Create first superuser if not exists"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if superuser already exists
            result = await db.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✓ Superuser {settings.FIRST_SUPERUSER_EMAIL} already exists")
                return
            
            # Create superuser
            user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                full_name="Admin User",
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role="admin",
                is_superuser=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
            print(f"✓ Superuser created: {settings.FIRST_SUPERUSER_EMAIL}")
            print(f"  Password: {settings.FIRST_SUPERUSER_PASSWORD}")
            print(f"  ⚠️  Please change the password after first login!")
            
        except Exception as e:
            print(f"✗ Error creating superuser: {str(e)}")
            await db.rollback()
            raise


async def create_default_pipeline():
    """Create default sales pipeline"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if default pipeline exists
            result = await db.execute(
                select(Pipeline).where(Pipeline.is_default == True)
            )
            existing_pipeline = result.scalar_one_or_none()
            
            if existing_pipeline:
                print("✓ Default pipeline already exists")
                return
            
            # Create default pipeline
            pipeline = Pipeline(
                name="Default Sales Pipeline",
                description="Standard sales pipeline for crypto trading clients",
                is_default=True,
                is_active=True
            )
            db.add(pipeline)
            await db.flush()
            
            # Create stages
            stages = [
                {"name": "Lead", "description": "Initial contact", "order": 1, "probability": 10},
                {"name": "Qualification", "description": "Qualified lead", "order": 2, "probability": 25},
                {"name": "Presentation", "description": "Product demo", "order": 3, "probability": 50},
                {"name": "Proposal", "description": "Sent proposal", "order": 4, "probability": 75},
                {"name": "Negotiation", "description": "Contract negotiation", "order": 5, "probability": 90},
                {"name": "Closed Won", "description": "Client onboarded", "order": 6, "probability": 100},
            ]
            
            for stage_data in stages:
                stage = PipelineStage(
                    pipeline_id=pipeline.id,
                    **stage_data
                )
                db.add(stage)
            
            await db.commit()
            print(f"✓ Default pipeline created with {len(stages)} stages")
            
        except Exception as e:
            print(f"✗ Error creating pipeline: {str(e)}")
            await db.rollback()
            raise


async def main():
    """Main initialization function"""
    print("=" * 50)
    print("CryptoCRM Database Initialization")
    print("=" * 50)
    print()
    
    try:
        # Create tables
        await create_tables()
        print()
        
        # Create superuser
        await create_superuser()
        print()
        
        # Create default pipeline
        await create_default_pipeline()
        print()
        
        print("=" * 50)
        print("✓ Database initialization completed successfully!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Start backend: uvicorn app.main:app --reload")
        print("2. Start celery: celery -A app.worker.celery_app worker --pool=solo")
        print("3. Start frontend: cd ../frontend && npm start")
        print()
        
    except Exception as e:
        print()
        print("=" * 50)
        print(f"✗ Initialization failed: {str(e)}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

