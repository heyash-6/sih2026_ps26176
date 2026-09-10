import pytest
from app.orchestrator import orchestrator

def test_killer_demo_query_e2e():
    query_text = "I am at Ratnagiri. I want to go fishing tomorrow at 5 AM for 6 hours. Which fishing zone should I choose?"
    res = orchestrator.process_query(session_id="e2e_killer_query", text=query_text)
    
    assert res.session_id == "e2e_killer_query"
    assert res.needs_clarification is False
    assert len(res.execution_trace) >= 5
    assert res.recommendation is not None
    assert res.recommendation.zone_id.startswith("PFZ-")
    assert len(res.evidence) > 0
    assert len(res.explanation_text) > 0
    assert len(res.map_payload.candidates) > 0
    assert res.disclaimer != ""

def test_multilingual_marathi_e2e():
    query_text = "उद्या सकाळी रत्नागिरीवरून समुद्रात जाणे सुरक्षित आहे का?"
    res = orchestrator.process_query(session_id="mr_e2e", text=query_text)
    assert res.language == "mr"
    assert res.recommendation is not None
    assert len(res.explanation_text) > 0

def test_multilingual_hindi_e2e():
    query_text = "क्या रत्नागिरी के पास कल सुबह मछली पकड़ने जाना सुरक्षित है?"
    res = orchestrator.process_query(session_id="hi_e2e", text=query_text)
    assert res.language == "hi"
    assert res.recommendation is not None
    assert len(res.explanation_text) > 0
