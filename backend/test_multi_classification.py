import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.services.gemini_service import gemini_service

async def test():
    tests = [
        ('Billing question', 'Why was I charged twice?'),
        ('Technical issue', 'The app keeps crashing'),
        ('Complaint', 'Your service is terrible'),
    ]
    
    for subject, desc in tests:
        result = await gemini_service.classify_ticket(subject, desc)
        cat = result.get('category', 'N/A')
        conf = result.get('confidence_score', 0)
        print(f'OK {subject:20} -> {cat:20} ({conf:.2f})')

asyncio.run(test())
