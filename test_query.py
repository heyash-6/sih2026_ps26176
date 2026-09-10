import json
from app.orchestrator import orchestrator

def run_test():
    print("=" * 60)
    print("🌊 Testing ORCA Marine Intelligence Agent Pipeline")
    print("=" * 60)

    # 1. English Killer Demo Query
    print("\n[Test 1] English Query:")
    query_text = "I am at Ratnagiri. I want to go fishing tomorrow at 5 AM for 6 hours. Which fishing zone should I choose?"
    print(f"User: {query_text}")
    res1 = orchestrator.process_query(session_id="test_en_01", text=query_text)
    
    print(f"\nDetected Language: {res1.language}")
    print("\n🤖 Agent Execution Trace:")
    for step in res1.execution_trace:
        print(f"  ✓ Step {step.get('step')}: {step.get('tool')} ({step.get('duration_ms')}ms) - {step.get('details')}")

    if res1.recommendation:
        print(f"\n🎯 Recommendation: {res1.recommendation.zone_id} (Status: {res1.recommendation.status.value}, Risk Score: {res1.recommendation.risk_score}/100, Band: {res1.recommendation.risk_band.value})")

    print("\n📊 Evidence Trail:")
    for ev in res1.evidence:
        print(f"  • {ev.claim} [{ev.source}]")

    print(f"\n💬 Explanation Prose:\n{res1.explanation_text}")
    print(f"\n⚠️ Disclaimer:\n{res1.disclaimer}")

    # 2. Marathi Multilingual Query
    print("\n" + "=" * 60)
    print("[Test 2] Marathi Multilingual Query:")
    mr_query = "उद्या सकाळी रत्नागिरीवरून समुद्रात जाणे सुरक्षित आहे का?"
    print(f"User: {mr_query}")
    res2 = orchestrator.process_query(session_id="test_mr_01", text=mr_query)
    print(f"\nDetected Language: {res2.language}")
    print(f"💬 Marathi Explanation Prose:\n{res2.explanation_text}")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
