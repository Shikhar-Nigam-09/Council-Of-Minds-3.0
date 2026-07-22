from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"success": True, "data": {"status": "ok", "database": "connected"}}
    except Exception as e:
        return {"success": False, "error": {"code": "DATABASE_ERROR", "message": "Database disconnected"}}
