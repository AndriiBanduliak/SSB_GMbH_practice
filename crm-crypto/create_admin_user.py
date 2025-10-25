"""
Admin-Benutzer mit derselben Passwort-Hash-Methode wie beim Login erstellen
"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash, verify_password

async def create_admin():
    """Admin-Benutzer mit korrekt gehashtem Passwort erstellen"""
    async with AsyncSessionLocal() as db:
        try:
            # Bestehenden Admin löschen
            await db.execute(
                text("DELETE FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            print("✓ Alter Admin-Benutzer entfernt")
            
            # Passwort-Hash mit DERSELBEN Funktion wie beim Login erstellen
            password = "admin123"
            hashed = get_password_hash(password)
            
            print(f"✓ Passwort-Hash erstellt: {hashed[:30]}...")
            
            # Verifizierung prüfen
            if verify_password(password, hashed):
                print("✓ Passwort-Verifizierung FUNKTIONIERT!")
            else:
                print("✗ Passwort-Verifizierung FEHLGESCHLAGEN!")
                return
            
            # Admin-Benutzer einfügen
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
                    "full_name": "Admin-Benutzer",
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
            print("✓ Admin-Benutzer erfolgreich erstellt!")
            print("=" * 60)
            print("  E-Mail:   admin@cryptocrm.com")
            print("  Passwort: admin123")
            print("=" * 60)
            print("")
            print("Jetzt versuchen Sie sich anzumelden unter http://localhost:3000")
            print("")
            
            # Benutzer in Datenbank verifizieren
            result = await db.execute(
                text("SELECT email, role, is_active FROM users WHERE email = 'admin@cryptocrm.com'")
            )
            user = result.first()
            if user:
                print(f"✓ Benutzer in Datenbank verifiziert: {user.email} (Rolle: {user.role}, aktiv: {user.is_active})")
            
        except Exception as e:
            print(f"✗ Fehler: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    print("Erstelle Admin-Benutzer mit app.core.security Funktionen...")
    print("")
    asyncio.run(create_admin())


