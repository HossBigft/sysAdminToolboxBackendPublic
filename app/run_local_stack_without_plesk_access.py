from unittest.mock import patch
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from tests.utils.container_db_utils import TestMariadb, TEST_DB_CMD
from tests.utils.container_unix_utils import UnixContainer

example.com


# Custom unique ID generator function for routes
def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# Initialize Sentry SDK if not in local environment
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    import sentry_sdk

    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set up CORS middleware if configured
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


testdb = TestMariadb().populate_db()
linux_container = UnixContainer().prepare_zonefile()


def mock_batch_ssh(command: str):
    stdout = testdb.run_cmd(command)
    return [{"host": TEST_SSH_HOST, "stdout": stdout}]


def mock_batch_ssh_ns(command: str):
    stdout = linux_container.run_cmd(command)
    return [{"host": TEST_SSH_HOST, "stdout": stdout}]


def mock_get_plesk_subscription_login_link_by_id(arg1, arg2, arg3):
    return f"https://{TEST_SSH_HOST}/login?secret=sdfdfsdfSECRET&success_redirect_url=%2Fadmin%2Fsubscription%2Foverview%2Fid%2F12345"


patches = [
    patch("app.plesk.ssh_utils.PLESK_DB_RUN_CMD_TEMPLATE", TEST_DB_CMD),
    patch(
        "app.plesk.ssh_utils.batch_ssh_execute",
        wraps=mock_batch_ssh,
    ),
    patch("app.dns.ssh_utils.batch_ssh_execute", wraps=mock_batch_ssh_ns),
    patch(
        "app.plesk.ssh_utils.plesk_generate_subscription_login_link",
        wraps=mock_get_plesk_subscription_login_link_by_id,
    ),
]

for p in patches:
    p.start()

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
