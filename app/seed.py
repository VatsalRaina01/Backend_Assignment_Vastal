"""
Database seed script.

Populates the database with realistic demo data:
- 3 users (admin, analyst, viewer) with known passwords
- 60+ financial records across 8 categories spanning 12 months

Run: python -m app.seed

This creates a rich dataset that makes the dashboard endpoints
interesting to explore via Swagger.
"""

import random
from datetime import date, timedelta

from app.database import SessionLocal, init_db
from app.models.record import FinancialRecord, RecordType
from app.models.user import User, UserRole, UserStatus
from app.utils.security import hash_password

# ── Demo Users ───────────────────────────────────────────────────────────────

DEMO_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123456",
        "name": "Alex Admin",
        "role": UserRole.ADMIN,
    },
    {
        "email": "analyst@example.com",
        "password": "analyst123456",
        "name": "Anna Analyst",
        "role": UserRole.ANALYST,
    },
    {
        "email": "viewer@example.com",
        "password": "viewer123456",
        "name": "Victor Viewer",
        "role": UserRole.VIEWER,
    },
]

# ── Realistic Financial Record Templates ─────────────────────────────────────

# Each template: (type, category, amount_range, description_templates)
RECORD_TEMPLATES = [
    # Income sources
    (
        "income", "Salary", (4500, 6000),
        [
            "Monthly salary payment",
            "Salary deposit - direct transfer",
            "Monthly compensation",
        ],
    ),
    (
        "income", "Freelance", (500, 3000),
        [
            "Freelance web development project",
            "Consulting fee - client engagement",
            "UI/UX design contract payment",
            "Technical writing assignment",
            "Mobile app development milestone",
        ],
    ),
    (
        "income", "Investments", (100, 1500),
        [
            "Dividend payment - stock portfolio",
            "Interest earned - savings account",
            "Bond coupon payment",
            "Mutual fund distribution",
        ],
    ),
    (
        "income", "Other Income", (50, 500),
        [
            "Refund received",
            "Cashback reward",
            "Gift received",
            "Tax refund deposit",
        ],
    ),
    # Expense categories
    (
        "expense", "Housing", (1200, 2000),
        [
            "Monthly rent payment",
            "Rent - apartment lease",
            "Housing payment",
        ],
    ),
    (
        "expense", "Groceries", (150, 450),
        [
            "Weekly grocery shopping",
            "Supermarket - food & supplies",
            "Organic produce delivery",
            "Wholesale club - monthly stock up",
        ],
    ),
    (
        "expense", "Transportation", (50, 300),
        [
            "Gas station fill-up",
            "Monthly transit pass",
            "Ride-share to airport",
            "Car maintenance - oil change",
            "Parking fees - downtown",
        ],
    ),
    (
        "expense", "Utilities", (80, 250),
        [
            "Electricity bill",
            "Internet service - monthly",
            "Water & sewage bill",
            "Natural gas - heating",
            "Cell phone plan",
        ],
    ),
    (
        "expense", "Healthcare", (20, 500),
        [
            "Doctor visit - copay",
            "Pharmacy - prescription medication",
            "Dental cleaning",
            "Eye exam & contacts",
            "Health insurance premium",
        ],
    ),
    (
        "expense", "Entertainment", (15, 200),
        [
            "Movie tickets",
            "Streaming subscription - monthly",
            "Concert tickets",
            "Restaurant dinner - weekend",
            "Book purchase - online",
            "Gaming subscription",
        ],
    ),
    (
        "expense", "Education", (50, 500),
        [
            "Online course - Python advanced",
            "Professional certification exam",
            "Technical book purchase",
            "Conference registration",
            "Workshop fee",
        ],
    ),
    (
        "expense", "Insurance", (100, 400),
        [
            "Auto insurance - monthly premium",
            "Renter's insurance payment",
            "Life insurance premium",
        ],
    ),
]


def seed_database():
    """Seed the database with demo data."""
    print("=" * 60)
    print("  SEEDING DATABASE")
    print("=" * 60)

    # Initialize tables
    init_db()

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("\n⚠  Database already contains data. Skipping seed.")
            print("   To reseed, delete 'finance.db' and run again.")
            return

        # ── Create Users ─────────────────────────────────────────────
        print("\n📋 Creating demo users...")
        created_users = []
        for user_data in DEMO_USERS:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
                status=UserStatus.ACTIVE,
            )
            db.add(user)
            created_users.append(user)
            print(f"   ✓ {user.name} ({user.email}) — role: {user.role.value}")

        db.commit()

        # Use admin as the creator for all records
        admin_user = created_users[0]

        # ── Create Financial Records ─────────────────────────────────
        print("\n💰 Creating financial records...")

        # Generate records for the last 12 months
        today = date.today()
        record_count = 0

        for months_ago in range(12):
            # Calculate the month
            target_date = today.replace(day=1) - timedelta(days=months_ago * 30)

            for template in RECORD_TEMPLATES:
                record_type, category, (min_amt, max_amt), descriptions = template

                # Generate 1-3 records per category per month
                num_records = random.randint(1, 3)

                # Skip some categories randomly to create realistic variance
                if random.random() < 0.2:
                    continue

                for _ in range(num_records):
                    # Random day within the month
                    day = random.randint(1, 28)
                    record_date = target_date.replace(day=day)

                    # Ensure date isn't in the future
                    if record_date > today:
                        continue

                    amount = round(random.uniform(min_amt, max_amt), 2)
                    description = random.choice(descriptions)

                    record = FinancialRecord(
                        amount=amount,
                        type=RecordType(record_type),
                        category=category,
                        date=record_date,
                        description=description,
                        user_id=admin_user.id,
                    )
                    db.add(record)
                    record_count += 1

        db.commit()
        print(f"   ✓ Created {record_count} financial records across 12 months")

        # ── Summary ──────────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("  SEED COMPLETE!")
        print("=" * 60)
        print(f"\n  Users created:   {len(created_users)}")
        print(f"  Records created: {record_count}")
        print("\n  Demo credentials:")
        print("  ┌──────────────────────────────────────────────┐")
        for user_data in DEMO_USERS:
            print(f"  │ {user_data['role'].value:8s} │ {user_data['email']:25s} │ {user_data['password']} │")
        print("  └──────────────────────────────────────────────┘")
        print("\n  Start the server: uvicorn app.main:app --reload")
        print("  API docs:         http://localhost:8000/docs")
        print()

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
