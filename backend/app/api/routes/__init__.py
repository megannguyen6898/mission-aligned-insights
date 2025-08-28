
from .auth import router as auth_router
from .users import router as users_router
from .data import router as data_router
from .integrations import router as integrations_router
from .dashboards import router as dashboards_router
from .reports import router as reports_router, templates_router as report_templates_router
from .investors import router as investors_router

__all__ = [
    "auth_router",
    "users_router", 
    "data_router",
    "integrations_router",
    "dashboards_router",
    "reports_router",
    "report_templates_router",
    "investors_router"
]
