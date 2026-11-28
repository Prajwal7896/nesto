# Nesto Database & Auth Documentation

## Overview

Nesto uses **SQLAlchemy ORM** to interface with PostgreSQL or SQLite databases. The database layer stores user registration credentials, profile data, subscription plans, and system timestamps.

---

## Database Configuration

The database configuration is loaded from environment variables using `python-dotenv`:

```python
# backend/db/models.py
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

---

## Entity Relationship & Table Schema

### Table: `users`

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `INTEGER` | Primary Key, Indexed | Auto-incrementing unique user identifier |
| `name` | `VARCHAR(100)` | `NOT NULL` | User full name |
| `email` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` | User primary email address |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Bcrypt hashed password string |
| `phone_number` | `VARCHAR(15)` | `UNIQUE`, `NULLABLE` | Optional contact phone number |
| `age` | `INTEGER` | `NULLABLE` | Optional user age |
| `role` | `VARCHAR(50)` | `NULLABLE`, Default: `'User'` | User account role |
| `image_url` | `TEXT` | `NULLABLE` | Path to uploaded profile image (`/static/uploads/...`) |
| `subscription_plan` | `VARCHAR(20)` | Default: `'FREE'` | Active subscription tier (`FREE`, `PRO`) |
| `created_at` | `TIMESTAMP` | Default: `NOW()` | Account creation timestamp |
| `updated_at` | `TIMESTAMP` | Default: `NOW()`, OnUpdate | Last profile update timestamp |

---

## Authentication Lifecycle & Security

1. **Password Hashing**: Passwords are encrypted using Passlib with `bcrypt`:
   ```python
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   hashed_password = pwd_context.hash(password)
   ```
2. **Credential Verification**:
   ```python
   user = db.query(User).filter(User.email == email).first()
   if not user or not pwd_context.verify(password, user.password_hash):
       # Invalid credentials
   ```
3. **Session Management**: Each endpoint receives a scoped database session injected via FastAPI dependency `get_db()`.
