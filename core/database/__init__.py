from .base import url, engine, Base, metadata, SessionFactory
from .types import intpk, ImageFile
from .dependencies import get_session, SessionDep
from .mixins import TimeStampMixin

def load_models():
    import apps.users.models
    import apps.users.events
    import apps.optic.models


# Register every mapped class whenever the database package is imported. The
# relationship strings in individual model modules can then resolve without
# requiring callers to remember a separate bootstrap call.
load_models()
