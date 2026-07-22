import pytest
from app.council.weight_filter import filter_evidence

def test_filter_evidence():
    outputs = {
        "agent_a": {"status": "success", "summary": "A", "evidence_points": [{"id": "1"}, {"id": "2"}, {"id": "3"}]},
        "agent_b": {"status": "success", "summary": "B", "evidence_points": [{"id": "4"}, {"id": "5"}]},
        "agent_c": {"status": "failed", "summary": "", "evidence_points": []}
    }
    
    weights = {"agent_a": 50, "agent_b": 50, "agent_c": 0}
    
    res = filter_evidence(outputs, weights, max_total_items=12)
    
    assert res["agent_a"]["included_in_synthesis"] is True
    assert len(res["agent_a"]["evidence_points"]) == 3
    assert res["agent_b"]["included_in_synthesis"] is True
    assert len(res["agent_b"]["evidence_points"]) == 2
    assert res["agent_c"]["included_in_synthesis"] is False
