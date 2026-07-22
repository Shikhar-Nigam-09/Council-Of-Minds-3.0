import logging
import uuid
from app.graph.state import GraphState
from app.services.synthesis_service import SynthesisService
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

async def synthesize_node(state: GraphState, config: RunnableConfig) -> dict:
    logger.info(f"Running synthesize_node for message_id {state.get('message_id')}")
    
    stream_queue = config.get("configurable", {}).get("stream_queue")
    
    if state.get("status") == "retrieval_failed":
        if stream_queue:
            await stream_queue.put({"type": "error", "message": "Retrieval failed. Unable to answer."})
        return {"status": "failed"}
        
    if state.get("status") == "council_skipped":
        if stream_queue:
            await stream_queue.put({"type": "error", "message": "No agents succeeded or were enabled."})
        return {"status": "failed"}
        
    agent_output_ids = state.get("agent_output_ids", [])
    confirmed_config = state.get("confirmed_configuration", {})
    weights = confirmed_config.get("weights", {})
    question = state.get("question", "")
    message_id = uuid.UUID(state.get("message_id"))
    
    result = await SynthesisService.synthesize(
        agent_output_ids, question, weights, message_id, stream_queue
    )
    
    return {"status": result.get("status")}
