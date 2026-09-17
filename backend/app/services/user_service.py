import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

DEFAULT_USER_EMAIL = "student@aimastertutor.local"


async def get_or_create_default_user(db: AsyncSession) -> User:
    """
    Ensures a default student user exists in development to prevent
    foreign key constraint violations during ingestion.
    """
    stmt = select(User).where(User.email == DEFAULT_USER_EMAIL)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=uuid.uuid4(),
            email=DEFAULT_USER_EMAIL,
            full_name="Student Dev User",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user
