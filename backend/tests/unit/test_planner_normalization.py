import pytest
from app.services.planner_service import PlannerService

def test_normalize_weights():
    # Regular distribution
    weights = {"logical": 20, "practical": 20, "analytical": 20, "skeptical": 20, "ethics": 20}
    enabled = {k: True for k in weights}
    res = PlannerService._normalize_weights(weights, enabled)
    assert sum(res.values()) == 100
    assert res["logical"] == 20
    
    # Needs scaling
    weights = {"logical": 10, "practical": 10, "analytical": 10, "skeptical": 10, "ethics": 10}
    enabled = {k: True for k in weights}
    res = PlannerService._normalize_weights(weights, enabled)
    assert sum(res.values()) == 100
    assert res["logical"] == 20
    
    # Disabled agents forced to 0
    weights = {"logical": 50, "practical": 50, "analytical": 50, "skeptical": 50, "ethics": 50}
    enabled = {"logical": True, "practical": True, "analytical": False, "skeptical": False, "ethics": False}
    res = PlannerService._normalize_weights(weights, enabled)
    assert res["analytical"] == 0
    assert res["logical"] == 50
    assert sum(res.values()) == 100
    
    # Clamping out of bounds
    weights = {"logical": -10, "practical": 200, "analytical": 20, "skeptical": 20, "ethics": 20}
    enabled = {k: True for k in weights}
    res = PlannerService._normalize_weights(weights, enabled)
    assert sum(res.values()) == 100
    assert res["practical"] > res["logical"]
