from loguru import logger
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_user_id
import crud
import utils
import schemas
from typing import Optional


from templates.user_register_init_message import INIT_MESSAGE

router = APIRouter(route_class=LoggingContextRoute)


@router.get("/orgs")
async def user_orgs(s_sales_company_org_id: Optional[int] = None, db=Depends(get_db)):
    try:
        orgs = await crud.query_s_sales_company_orgs(db, s_sales_company_org_id)
        print(999, orgs)
        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
