from app.models.database import Base, engine
import os


def reset_database():
    """Drop all tables and recreate"""
    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() != "yes":
        print("Cancelled.")
        return

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")

    print("Creating fresh tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

    print("\n🎉 Database reset complete!")


if __name__ == "__main__":
    reset_database()
