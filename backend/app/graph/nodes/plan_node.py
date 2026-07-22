import logging
import uuid
from app.graph.state import GraphState
from app.services.planner_service import PlannerService
from app.db.session import async_session_maker
from app.repositories.council_configuration_repository import CouncilConfigurationRepository
from app.models.council_configuration import CouncilConfiguration, ConfigurationSource

logger = logging.getLogger(__name__)

async def plan_node(state: GraphState) -> dict:
    logger.info(f"Running plan_node for message_id {state.get('message_id')}")
    
    question = state["question"]
    document_context = state["document_context"]
    
    recommendation = await PlannerService.generate_plan(question, document_context)
    
    async with async_session_maker() as session:
        config_repo = CouncilConfigurationRepository(session)
        c_config = CouncilConfiguration(
            message_id=uuid.UUID(state["message_id"]),
            source=ConfigurationSource(recommendation["source"]),
            logical_weight=recommendation["weights"]["logical"],
            practical_weight=recommendation["weights"]["practical"],
            analytical_weight=recommendation["weights"]["analytical"],
            skeptical_weight=recommendation["weights"]["skeptical"],
            ethics_weight=recommendation["weights"]["ethics"],
            logical_enabled=recommendation["enabled"]["logical"],
            practical_enabled=recommendation["enabled"]["practical"],
            analytical_enabled=recommendation["enabled"]["analytical"],
            skeptical_enabled=recommendation["enabled"]["skeptical"],
            ethics_enabled=recommendation["enabled"]["ethics"],
            model_name=recommendation["model_name"],
            prompt_version=recommendation["prompt_version"],
            latency_ms=recommendation["latency_ms"],
            retry_count=recommendation["retry_count"]
        )
        await config_repo.save(c_config)
        await session.commit()
    
    return {
        "planner_recommendation": recommendation["weights"],
        "planner_source": recommendation["source"],
        "status": "awaiting_confirmation"
    }
