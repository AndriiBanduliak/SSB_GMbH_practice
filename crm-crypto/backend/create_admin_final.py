"""
Create admin user using the SAME password hashing as login
"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash, verify_password

async def create_admin():
    """Create admin user with properly hashed password"""
    async with AsyncSessionLocal() as db:
        try:
            # Delete existing admin
            await db.execute(
                text("DELETE FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            print("✓ Removed old admin user")
            
            # Create password hash using SAME function as login
            password = "admin123"
            hashed = get_password_hash(password)
            
            print(f"✓ Password hash created: {hashed[:30]}...")
            
            # Verify it works
            if verify_password(password, hashed):
                print("✓ Password verification WORKS!")
            else:
                print("✗ Password verification FAILED!")
                return
            
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
            
            print("")
            print("=" * 60)
            print("✓ Admin user created successfully!")
            print("=" * 60)
            print("  Email:    admin@cryptocrm.com")
            print("  Password: admin123")
            print("=" * 60)
            print("")
            print("Now try to login at http://localhost:3000")
            print("")
            
            # Verify user was created
            result = await db.execute(
                text("SELECT email, role, is_active FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            user = result.first()
            if user:
                print(f"✓ User verified in database: {user.email} (role: {user.role}, active: {user.is_active})")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    print("Creating admin user using app.core.security functions...")
    print("")
    asyncio.run(create_admin())

