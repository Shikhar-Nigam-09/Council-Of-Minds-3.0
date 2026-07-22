from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes.plan_node import plan_node
from app.graph.nodes.confirm_node import confirm_node
from app.graph.nodes.retrieve_node import retrieve_node
from app.graph.nodes.council_node import council_node
from app.graph.nodes.synthesize_node import synthesize_node

def get_compiled_graph(checkpointer):
    workflow = StateGraph(GraphState)
    
    workflow.add_node("plan_node", plan_node)
    workflow.add_node("confirm_node", confirm_node)
    workflow.add_node("retrieve_node", retrieve_node)
    workflow.add_node("council_node", council_node)
    workflow.add_node("synthesize_node", synthesize_node)
    
    workflow.set_entry_point("plan_node")
    workflow.add_edge("plan_node", "confirm_node")
    
    # Phase 4 Graph shape: plan_node -> interrupt -> confirm_node -> END
    # Phase 5 extends this to:
    # plan_node -> interrupt -> confirm_node -> retrieve_node -> council_node -> synthesize_node -> END
    workflow.add_edge("confirm_node", "retrieve_node")
    workflow.add_edge("retrieve_node", "council_node")
    workflow.add_edge("council_node", "synthesize_node")
    workflow.add_edge("synthesize_node", END)
    
    return workflow.compile(checkpointer=checkpointer, interrupt_before=["confirm_node", "retrieve_node"])
