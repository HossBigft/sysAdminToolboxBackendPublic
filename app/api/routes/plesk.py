from fastapi import APIRouter, HTTPException, Depends
from app.ssh_plesk_subscription_info_retriever import query_subscription_info_by_domain
from app.validators import validate_domain_name

PREFIX = "/plesk"

router = APIRouter(prefix=PREFIX)

@router.get("/get/subscription/")
async def find_plesk_subscription_by_domain(
    domain: str = Depends(validate_domain_name),
):
    subscriptions = await query_subscription_info_by_domain(domain)
    if not subscriptions:
        raise HTTPException(
            status_code=404, detail=f"Subscription with domain [{domain}] not found."
        )
    return subscriptions