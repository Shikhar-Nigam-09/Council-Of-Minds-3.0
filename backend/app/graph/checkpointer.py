import sys
from app.core.config import settings

checkpointer = None
_pool = None

async def get_checkpointer():
    global checkpointer, _pool
    if checkpointer is not None:
        return checkpointer

    if not settings.DATABASE_URL:
        return None
        
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    
    kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    from psycopg_pool import ConnectionPool
    from langgraph.checkpoint.postgres import PostgresSaver
    import asyncio
    
    class AsyncSafePostgresSaver(PostgresSaver):
        async def aget_tuple(self, config):
            return await asyncio.to_thread(self.get_tuple, config)
            
        async def aput(self, config, checkpoint, metadata, new_versions):
            return await asyncio.to_thread(self.put, config, checkpoint, metadata, new_versions)
            
        async def aput_writes(self, config, writes, task_id):
            return await asyncio.to_thread(self.put_writes, config, writes, task_id)
            
        async def alist(self, config, *, filter=None, before=None, limit=None):
            def _get_list():
                return list(self.list(config, filter=filter, before=before, limit=limit))
            results = await asyncio.to_thread(_get_list)
            for r in results:
                yield r

        async def aget(self, config):
            return await asyncio.to_thread(self.get, config)

        async def acopy_thread(self, from_thread_id, to_thread_id):
            return await asyncio.to_thread(self.copy_thread, from_thread_id, to_thread_id)

        async def adelete_for_runs(self, run_ids):
            return await asyncio.to_thread(self.delete_for_runs, run_ids)

        async def adelete_thread(self, thread_id):
            return await asyncio.to_thread(self.delete_thread, thread_id)

        async def aget_delta_channel_history(self, config, before=None, limit=None):
            def _get_hist():
                return list(self.get_delta_channel_history(config, before=before, limit=limit))
            results = await asyncio.to_thread(_get_hist)
            for r in results:
                yield r

        async def aprune(self, config, limit=None):
            return await asyncio.to_thread(self.prune, config, limit=limit)

    _pool = ConnectionPool(
        conninfo=db_url,
        max_size=20,
        kwargs=kwargs,
        open=False,
    )
    _pool.open()
    checkpointer = AsyncSafePostgresSaver(_pool)
    checkpointer.setup()
        
    return checkpointer

async def close_checkpointer():
    global _pool
    if _pool:
        _pool.close()
