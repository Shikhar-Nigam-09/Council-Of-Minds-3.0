import logging
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

async def confirm_node(state: GraphState) -> dict:
    logger.info(f"Running confirm_node for message_id {state.get('message_id')}")
    
    # This node strictly records the confirmed configuration into state and marks the turn as confirmed.
    # It MUST NOT contain any retrieval, council execution, or synthesis logic - now or ever.
    
    confirmed_configuration = state.get("confirmed_configuration")
    if not confirmed_configuration:
        logger.warning("No confirmed_configuration found in state!")
        
    return {
        "status": "confirmed"
    }
