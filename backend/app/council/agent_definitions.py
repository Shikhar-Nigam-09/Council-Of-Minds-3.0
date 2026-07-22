from pydantic import BaseModel, Field
from typing import List, Literal
import json

class EvidencePoint(BaseModel):
    claim: str = Field(..., description="The specific claim or finding from the text.")
    supporting_chunk_id: str = Field(..., description="The ID of the chunk that supports this claim.")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence in this claim.")

class AgentOutputSchema(BaseModel):
    summary: str = Field(..., description="A summary of the findings from this agent's unique perspective.")
    evidence_points: List[EvidencePoint] = Field(..., description="List of specific evidence points extracted.")

def get_agent_prompt(agent_name: str, question: str, chunks_text: str) -> str:
    base_prompt = "You are the {role} council member. {role_desc}\n\n"
    base_prompt += "Your task is to answer the user's question based ONLY on the provided chunks of text. "
    base_prompt += "You MUST ONLY cite chunk IDs that are explicitly provided in the context below. Do not hallucinate chunk IDs.\n\n"
    base_prompt += "User Question: {question}\n\n"
    base_prompt += "Context Chunks:\n{chunks_text}\n\n"
    base_prompt += "Return your response in valid JSON matching this schema:\n"
    base_prompt += "{schema}\n"
    
    roles = {
        "logical": ("Logical", "You focus on pure logic, structure, and identifying causal relationships."),
        "practical": ("Practical", "You focus on actionable, real-world application, and concrete steps."),
        "analytical": ("Analytical", "You focus on data, deep analysis, statistics, and verifiable facts."),
        "skeptical": ("Skeptical", "You focus on questioning assumptions, identifying biases, and highlighting missing information."),
        "ethics": ("Ethics & Society", "You focus on morality, fairness, societal impact, and ethical considerations.")
    }
    
    role, role_desc = roles.get(agent_name, ("General", "You provide general insight."))
    schema = AgentOutputSchema.model_json_schema()
    return base_prompt.format(role=role, role_desc=role_desc, question=question, chunks_text=chunks_text, schema=json.dumps(schema, indent=2))
