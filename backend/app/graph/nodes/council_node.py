import logging
import uuid
from app.graph.state import GraphState
from app.services.council_service import CouncilService
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

async def council_node(state: GraphState, config: RunnableConfig) -> dict:
    logger.info(f"Running council_node for message_id {state.get('message_id')}")
    
    stream_queue = config.get("configurable", {}).get("stream_queue")
    
    if state.get("status") == "retrieval_failed":
        logger.warning("Skipping council execution due to retrieval failure.")
        return {"status": "council_skipped", "agent_output_ids": []}
        
    chunk_ids = state.get("retrieved_chunk_ids", [])
    if not chunk_ids:
        logger.warning("No chunks retrieved.")
        
    question = state.get("question", "")
    confirmed_config = state.get("confirmed_configuration", {})
    message_id = uuid.UUID(state.get("message_id"))
    
    agent_output_ids = await CouncilService.run_council(chunk_ids, question, confirmed_config, message_id, stream_queue)
    
    if not agent_output_ids:
        return {"status": "council_skipped", "agent_output_ids": []}
        
    return {"status": "council_completed", "agent_output_ids": agent_output_ids}
