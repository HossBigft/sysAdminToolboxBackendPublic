import re
from fastapi import HTTPException

from app.host_lists import PLESK_SERVER_LIST
from app.ssh_async_executor import run_command_over_ssh

PLESK_LOGLINK_CMD = "plesk login"
LINUX_USERNAME_PATTERN = r"^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$"
REDIRECTION_HEADER = r"&success_redirect_url=%2Fadmin%2Fsubscription%2Foverview%2Fid%2F"


async def _is_valid_username(ssh_username: str) -> bool:
    return bool(re.match(LINUX_USERNAME_PATTERN, ssh_username))


async def _build_login_command(ssh_username: str) -> str:
    return f"plesk login {ssh_username}"


async def _is_subscription_id_exist(host: str, subscriptionId: str) -> bool:
    get_subscription_name_cmd = f'plesk db -Ne "SELECT name FROM domains WHERE webspace_id=0 AND id={subscriptionId}"'
    result = await run_command_over_ssh(host, get_subscription_name_cmd)
    subscription_name = result["stdout"]
    return not subscription_name == ""


async def get_plesk_login_link(host: str, ssh_username: str) -> str:
    if host not in PLESK_SERVER_LIST:
        raise ValueError(f"Host '{host}' is not Plesk server.")
    if not await _is_valid_username(ssh_username):
        raise ValueError("Input string should be a valid linux username.")
    cmd_to_run = await _build_login_command(ssh_username)
    result = await run_command_over_ssh(host, cmd_to_run)
    login_link = result["stdout"]
    return login_link


async def get_plesk_subscription_login_link_by_id(
    host: str, subscription_id: int, ssh_username: str
) -> str:
    if host not in PLESK_SERVER_LIST:
        raise HTTPException(
            status_code=400, detail=f"Host '{host}' is not a Plesk server."
        )

    if not await _is_valid_username(ssh_username):
        raise HTTPException(
            status_code=400, detail="Input string should be a valid Linux username."
        )

    if not await _is_subscription_id_exist(host, subscription_id):
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with {subscription_id} ID doesn't exist.",
        )

    plesk_login_link = await get_plesk_login_link(host, ssh_username)
    subscription_login_link = f"{plesk_login_link}{REDIRECTION_HEADER}{subscription_id}"

    return subscription_login_link
