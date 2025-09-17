from fastapi import APIRouter, Query

from src.services.verification import Verifier


router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("", summary="校验本地数据文件（支持每篇内容明细）")
async def verify_local(detail: bool = Query(False, description="是否返回每篇内容的明细问题列表")):
    v = Verifier()
    return v.verify(detail=detail)
