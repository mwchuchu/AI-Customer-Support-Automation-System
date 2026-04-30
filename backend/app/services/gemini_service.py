"""
Gemini AI Service — Core LLM engine for the support pipeline.
Handles: classification, sentiment analysis, response generation, escalation decisions.
"""
import time
import json
import re
from typing import Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class   GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.model_name = settings.GEMINI_MODEL

    def _extract_json(self, text: str) -> dict:
        """Safely extract JSON from model response."""
        # Remove markdown fences
        cleaned = re.sub(r"```(?:json)?", "", text).strip()
        cleaned = cleaned.replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                candidate = match.group()
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # Last attempt: normalize single quotes to double quotes for loose JSON
                    normalized = candidate.replace("'", '"')
                    return json.loads(normalized)
            raise ValueError(f"Could not parse JSON from response: {text[:200]}")

    def _validate_classification(self, data: dict) -> dict:
        allowed_categories = {
            "billing_inquiry",
            "account_info",
            "password_reset",
            "order_status",
            "technical_issue",
            "complaint",
            "feature_request",
            "faq",
            "other",
        }
        allowed_priorities = {"low", "medium", "high", "critical"}
        allowed_sentiments = {"positive", "neutral", "negative", "frustrated", "urgent"}

        category = data.get("category")
        priority = data.get("priority")
        sentiment = data.get("sentiment")
        confidence = data.get("confidence_score")
        summary = data.get("summary")
        tags = data.get("tags")

        if category not in allowed_categories:
            raise ValueError(f"Invalid category: {category}")
        if priority not in allowed_priorities:
            raise ValueError(f"Invalid priority: {priority}")
        if sentiment not in allowed_sentiments:
            raise ValueError(f"Invalid sentiment: {sentiment}")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(f"Invalid confidence_score: {confidence}")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("Invalid summary")
        if not isinstance(tags, list):
            raise ValueError("Invalid tags")

        data["confidence_score"] = float(confidence)
        data["summary"] = summary.strip()
        return data

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_model(self, prompt: str) -> tuple[str, int]:
        """Call Gemini model with retry logic. Returns (response_text, tokens_used)."""
        start = time.time()
        response = self.model.generate_content(prompt)
        latency_ms = int((time.time() - start) * 1000)
        text = response.text
        tokens = getattr(response.usage_metadata, "total_token_count", 0)
        return text, tokens, latency_ms

    async def classify_ticket(self, subject: str, description: str) -> dict:
        """
        Step 1: Classify ticket category, priority, sentiment, and confidence.
        Returns structured classification data.
        """
        prompt = f"""You are an expert customer support AI classifier.

Analyze this support ticket and return ONLY a valid JSON object with no extra text.

TICKET:
Subject: {subject}
Description: {description}

Return this exact JSON structure:
{{
  "category": "<one of: billing_inquiry|account_info|password_reset|order_status|technical_issue|complaint|feature_request|faq|other>",
  "priority": "<one of: low|medium|high|critical>",
  "sentiment": "<one of: positive|neutral|negative|frustrated|urgent>",
  "confidence_score": <float between 0.0 and 1.0>,
  "summary": "<1-2 sentence summary of the issue>",
  "tags": ["<tag1>", "<tag2>"],
  "requires_human": <true|false>,
  "escalation_reason": "<reason if requires_human is true, else null>"
}}

Rules:
- critical priority: system down, data loss, security breach, legal threats
- high priority: major features broken, payments failing, account locked
- medium priority: partial functionality issues, billing questions
- low priority: general inquiries, feature requests, feedback
- requires_human: true ONLY if sentiment is frustrated/urgent AND issue involves legal/financial disputes, account security breaches, or complex technical problems requiring code changes. For simple issues like password resets, billing questions, order status, basic technical support, or FAQs, set requires_human to false.
"""
        try:
            text, tokens, latency = await self._call_model(prompt)
            data = self._extract_json(text)
            data = self._validate_classification(data)
            data["tokens_used"] = tokens
            data["latency_ms"] = latency
            logger.info("Ticket classified", category=data.get("category"), confidence=data.get("confidence_score"))
            return data
        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return {
                "category": "other",
                "priority": "medium",
                "sentiment": "neutral",
                "confidence_score": 0.0,
                "summary": "Classification failed",
                "tags": [],
                "requires_human": True,
                "escalation_reason": f"AI classification error: {str(e)}",
                "tokens_used": 0,
                "latency_ms": 0,
            }

    async def generate_response(
        self,
        subject: str,
        description: str,
        category: str,
        sentiment: str,
        priority: str,
    ) -> dict:
        """
        Step 2: Generate a professional, empathetic customer response.
        Returns the response text and confidence.
        """
        tone_guide = {
            "frustrated": "very empathetic, apologetic, and solution-focused",
            "urgent": "immediate, action-oriented, and reassuring",
            "negative": "empathetic and professional",
            "positive": "warm and helpful",
            "neutral": "professional and informative",
        }
        tone = tone_guide.get(sentiment, "professional")

        prompt = f"""You are a professional customer support agent for a technology company.

Write a response to this support ticket. Be {tone}.

TICKET DETAILS:
Subject: {subject}
Description: {description}
Category: {category}
Priority: {priority}

Return ONLY a valid JSON object:
{{
  "response_text": "<your full customer-facing response here>",
  "confidence_score": <float 0.0-1.0 — how confident you are this response adequately addresses the customer's immediate needs and provides clear next steps>,
  "resolution_steps": ["<step 1>", "<step 2>"],
  "follow_up_required": <true|false>
}}

Guidelines:
- Start with acknowledgment of the customer's issue
- Be specific and actionable
- Provide clear next steps
- For simple issues (billing, account info, password reset, order status, basic technical support), provide complete resolution steps
- For complex issues, acknowledge the problem and explain next steps clearly
- End with an offer for further assistance
- Keep it under 200 words
- Do NOT make up specific account details or order numbers
"""
        try:
            text, tokens, latency = await self._call_model(prompt)
            data = self._extract_json(text)
            data["tokens_used"] = tokens
            data["latency_ms"] = latency
            logger.info("Response generated", confidence=data.get("confidence_score"))
            return data
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            return {
                "response_text": (
                    "Thank you for contacting us. We have received your request and our team "
                    "will review it shortly. A support agent will reach out to you within 24 hours."
                ),
                "confidence_score": 0.5,
                "resolution_steps": [],
                "follow_up_required": True,
                "tokens_used": 0,
                "latency_ms": 0,
            }

    async def decide_escalation(
        self,
        classification: dict,
        response_confidence: float,
    ) -> dict:
        """
        Step 3: Make the final escalation decision based on classification + response confidence.
        """
        should_auto_resolve = (
            not classification.get("requires_human", True)
            and classification.get("category") in settings.AUTO_RESOLVE_CATEGORIES
            and classification.get("confidence_score", 0) >= settings.AI_CONFIDENCE_THRESHOLD
            and response_confidence >= settings.AI_CONFIDENCE_THRESHOLD
        )

        return {
            "auto_resolve": should_auto_resolve,
            "escalate": not should_auto_resolve,
            "reason": classification.get("escalation_reason") or (
                None if should_auto_resolve else "Issue complexity requires human review"
            ),
        }


gemini_service = GeminiService()
