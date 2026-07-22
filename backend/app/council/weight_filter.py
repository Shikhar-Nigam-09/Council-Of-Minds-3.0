from typing import Dict, Any, List

def filter_evidence(agent_outputs: Dict[str, Dict[str, Any]], weights: Dict[str, int], max_total_items: int = 12) -> Dict[str, Any]:
    """
    Deterministically filters evidence based on weight.
    Pure function, no LLM calls.
    """
    filtered_bundle = {}
    
    for agent, output in agent_outputs.items():
        weight = weights.get(agent, 0)
        
        if output.get("status") != "success" or weight <= 0:
            filtered_bundle[agent] = {
                "weight_used": weight,
                "included_in_synthesis": False
            }
            continue
            
        evidence_points = output.get("evidence_points", [])
        
        allowed_items = round((weight / 100.0) * max_total_items)
        
        selected_evidence = evidence_points[:allowed_items]
        
        if selected_evidence:
            filtered_bundle[agent] = {
                "summary": output.get("summary"),
                "evidence_points": selected_evidence,
                "weight_used": weight,
                "included_in_synthesis": True
            }
        else:
            filtered_bundle[agent] = {
                "weight_used": weight,
                "included_in_synthesis": False
            }
            
    return filtered_bundle
