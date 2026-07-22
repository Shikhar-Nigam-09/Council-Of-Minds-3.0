"""
GraphState is a locked contract: it holds ONLY identifiers (conversation_id, message_id, document_ids, graph_thread_id) 
and small structured data (planner_recommendation, confirmed_configuration, status).
It must NEVER hold raw chunk text, retrieved document content, or full LLM completions.
Nodes must fetch large data independently during execution using the identifiers stored here.
"""
from typing import TypedDict, Dict, Any, Optional

class GraphState(TypedDict):
    conversation_id: str
    message_id: str
    document_id: str
    question: str
    document_context: Dict[str, Any]
    planner_recommendation: Optional[Dict[str, Any]]
    planner_source: Optional[str]
    confirmed_configuration: Optional[Dict[str, Any]]
    status: str
    retrieved_chunk_ids: Optional[list[str]]
    agent_output_ids: Optional[list[str]]
