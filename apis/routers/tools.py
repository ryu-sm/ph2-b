from fastapi import APIRouter
import utils
from core.config import settings

router = APIRouter()


@router.post("/link-for-qrcode/{org_id}")
async def gen_link_for_qrcode(org_id: int):
    data = {"s_sales_company_org_id": f"{org_id}"}
    token = utils.gen_token(data, 525600)
    return f"{settings.FRONTEND_BASE_URL}?token={token}"
