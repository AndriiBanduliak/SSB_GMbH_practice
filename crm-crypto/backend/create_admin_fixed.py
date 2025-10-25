"""
Create admin user with working password hash
"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
import bcrypt

async def create_admin():
    """Create admin user with properly hashed password"""
    async with AsyncSessionLocal() as db:
        try:
            # Delete existing admin if exists
            await db.execute(
                text("DELETE FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            print("✓ Removed old admin user (if existed)")
            
            # Create password hash using current bcrypt
            password = "admin123"
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            print(f"✓ Password hash created: {hashed[:20]}...")
            
            # Insert admin user
            await db.execute(
                text("""
                INSERT INTO users (email, full_name, hashed_password, role, is_2fa_enabled, is_active, is_superuser, created_at)
                VALUES (
                    :email,
                    :full_name,
                    :hashed_password,
                    :role,
                    :is_2fa_enabled,
                    :is_active,
                    :is_superuser,
                    NOW()
                )
                """),
                {
                    "email": "admin@cryptocrm.com",
                    "full_name": "Admin User",
                    "hashed_password": hashed,
                    "role": "ADMIN",
                    "is_2fa_enabled": False,
                    "is_active": True,
                    "is_superuser": True
                }
            )
            await db.commit()
            
            print("=" * 50)
            print("✓ Admin user created successfully!")
            print("=" * 50)
            print("  Email:    admin@cryptocrm.com")
            print("  Password: admin123")
            print("=" * 50)
            print("")
            print("Now try to login at http://localhost:3000")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin())

