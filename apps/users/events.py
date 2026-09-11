from sqlalchemy import event
from sqlalchemy.orm import Session

from apps.users.models import User, UserSettings


@event.listens_for(Session, "before_flush")
def create_missing_user_settings(session: Session, flush_context, instances) -> None:
    for obj in session.new:
        if isinstance(obj, User) and obj.settings is None:
            obj.settings = UserSettings()
