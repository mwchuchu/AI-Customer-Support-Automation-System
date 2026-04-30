import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.gemini_service import gemini_service

async def test_simple_ticket():
    print("Testing simple ticket that should auto-resolve...")
    result = await gemini_service.classify_ticket(
        'How do I reset my password?',
        'I forgot my password and need to reset it. Can you help me with the steps?'
    )
    print('Classification result:')
    print('Category:', result.get('category'))
    print('Priority:', result.get('priority'))
    print('Sentiment:', result.get('sentiment'))
    print('Confidence:', result.get('confidence_score'))
    print('Requires human:', result.get('requires_human'))
    print('Summary:', result.get('summary'))

    # Test response generation
    response = await gemini_service.generate_response(
        subject='How do I reset my password?',
        description='I forgot my password and need to reset it. Can you help me with the steps?',
        category=result.get('category'),
        sentiment=result.get('sentiment'),
        priority=result.get('priority')
    )
    print('\nResponse generation:')
    print('Confidence:', response.get('confidence_score'))
    print('Follow up required:', response.get('follow_up_required'))

    # Test escalation decision
    decision = await gemini_service.decide_escalation(result, response.get('confidence_score'))
    print('\nEscalation decision:')
    print('Auto resolve:', decision.get('auto_resolve'))
    print('Reason:', decision.get('reason'))

if __name__ == "__main__":
    asyncio.run(test_simple_ticket())