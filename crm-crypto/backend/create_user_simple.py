"""
Simple script to create admin user
"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def create_admin():
    """Create admin user with pre-hashed password"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if user exists
            result = await db.execute(
                text("SELECT email FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            existing = result.first()
            
            if existing:
                print("✓ Admin user already exists!")
                return
            
            # Insert admin user with pre-hashed password for 'admin123'
            await db.execute(
                text("""
                INSERT INTO users (email, full_name, hashed_password, role, is_2fa_enabled, is_active, is_superuser, created_at)
                VALUES (
                    'admin@cryptocrm.com',
                    'Admin User',
                    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ygPCLDBJzRGy',
                    'ADMIN',
                    false,
                    true,
                    true,
                    NOW()
                )
                """)
            )
            await db.commit()
            print("✓ Admin user created successfully!")
            print("  Email: admin@cryptocrm.com")
            print("  Password: admin123")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin())

