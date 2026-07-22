import logging
from app.graph.state import GraphState
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

async def retrieve_node(state: GraphState) -> dict:
    logger.info(f"Running retrieve_node for message_id {state.get('message_id')}")
    
    question = state.get("question", "")
    document_id = state.get("document_id")
    
    if not document_id:
        logger.error("Missing document_id in state")
        return {"status": "retrieval_failed", "retrieved_chunk_ids": []}
        
    try:
        chunk_ids = await RetrievalService.retrieve_chunks(document_id, question)
        return {"retrieved_chunk_ids": chunk_ids, "status": "retrieved"}
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {"status": "retrieval_failed", "retrieved_chunk_ids": []}
