import pytest
from app.schemas.nlu import NLUInput, IntentEnum
from app.agents.nlu_agent import nlu_agent

def test_nlu_english_safety_check():
    inp = NLUInput(session_id="t1", text="Is it safe to venture into the sea tomorrow morning?")
    out = nlu_agent.process(inp)
    assert out.language == "en"
    assert out.intent == IntentEnum.SAFETY_CHECK
    assert out.entities.date is not None

def test_nlu_marathi_safety_check():
    inp = NLUInput(session_id="t2", text="उद्या सकाळी समुद्रात जाणे सुरक्षित आहे का?")
    out = nlu_agent.process(inp)
    assert out.language == "mr"
    assert out.intent == IntentEnum.SAFETY_CHECK

def test_nlu_hindi_pfz_lookup():
    inp = NLUInput(session_id="t3", text="मुझे कल सुबह रत्नागिरी में मछली पकड़ने जाना है, क्या यह सुरक्षित है?")
    out = nlu_agent.process(inp)
    assert out.language == "hi"
    assert out.entities.location_text == "Ratnagiri"

def test_nlu_missing_location_clarification():
    inp = NLUInput(session_id="t4", text="Where is the nearest PFZ today?")
    out = nlu_agent.process(inp)
    assert out.needs_clarification is True
    assert out.clarification_question is not None
