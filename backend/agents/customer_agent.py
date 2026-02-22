from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from backend.config import get_settings
from backend.rag.qdrant_client import search_all_collections
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )


class CustomerAgent:
    def __init__(self):
        self.llm = get_llm()
        self.system_prompt = """You are a helpful and friendly tyre specialist at Matrax Tyres. 

CONVERSATION FLOW:
1. When a customer mentions their car brand → Greet them warmly and ask for the specific model and year
2. When you identify their car model → Present the compatible tyre sizes as a simple list and ask which size they need
3. If exact model not found but SIMILAR models exist → Suggest the similar models found in database
4. When they specify a tyre size (or if there's only ONE size for their car) → Recommend 2-3 suitable tyres with prices
5. When they ask about a specific size → Show available tyres for that exact size

IMPORTANT - HANDLING SIMILAR MATCHES:
- If customer asks for "C-Class" but we have "E-Class" → Suggest it! ("I don't have C-Class but I found E-Class...")
- ALWAYS show alternative models from the same brand if exact model not available
- Use the search results provided - they're ranked by similarity

RESPONSE STYLE:
- Be warm, natural, and conversational (like a helpful friend, not a robot)
- Keep responses SHORT and focused (2-3 sentences max, then specific info)
- Use simple, everyday language
- NEVER mention database IDs or technical system details or similarity scores
- Format prices clearly with currency symbol
- Use bullet points for lists (• not *)
- Add emojis sparingly for warmth (🚗 💰 ✅)

WHEN SHOWING TYRES:
Format: **Brand Model** - Size | Type | £Price | Stock available
Example: **Michelin Pilot Sport** - 225/50R17 | Performance | £149.99 | In stock

Keep it friendly and helpful!"""

    async def process_message(self, user_message: str, chat_history: list[dict] = None) -> dict:
        logger.info(f"\n{'='*80}")
        logger.info(f"[CUSTOMER AGENT] Processing message: '{user_message}'")
        logger.info(f"[CUSTOMER AGENT] Chat history length: {len(chat_history) if chat_history else 0}")
        
        # Build context from last 6 messages for better understanding
        context_messages = []
        context_for_search = []
        if chat_history:
            recent_msgs = chat_history[-6:]  # Last 6 messages
            for msg in recent_msgs:
                role = "Customer" if msg.get('sender') == 'user' else "Agent"
                text = msg.get('text', '')
                context_messages.append(f"{role}: {text}")
                # Extract any tyre sizes or important data for search context
                context_for_search.append(text)
            logger.info(f"[CUSTOMER AGENT] Context from last {len(recent_msgs)} messages included")
        
        # Build intelligent search query: combine user message with recent context
        # This helps when user says vague things like "first one" or "yes"
        if len(user_message.split()) <= 3:  # Short messages likely need context
            # Combine with recent context for better search
            search_query = f"{user_message} {' '.join(context_for_search[-2:])}"  # Last 2 messages as context
            logger.info(f"[CUSTOMER AGENT] Short message detected, enhanced search: '{search_query[:100]}...'")
        else:
            search_query = user_message
        
        rag_results = search_all_collections(search_query, limit=5)
        logger.info(f"[CUSTOMER AGENT] RAG search completed")

        context_parts = []
        extracted_info = {
            "car_brands": [],
            "car_models": [],
            "tyre_brands": [],
            "tyres": [],
        }

        for collection, results in rag_results.items():
            if results:
                logger.info(f"[CUSTOMER AGENT] {collection}: Found {len(results)} results")
                context_parts.append(f"\n{collection.upper()}:")
                for r in results:
                    # Show results with score > 0.25 to catch similar matches
                    if r["score"] > 0.25:
                        payload = r["payload"]
                        extracted_info[collection].append(payload)
                        
                        # Include similarity indicator for the agent
                        match_type = "Exact match" if r["score"] > 0.7 else "Similar match"
                        
                        logger.info(f"[CUSTOMER AGENT]   - Score: {r['score']:.3f} | {match_type} | {payload.get('name', payload.get('model', 'Unknown'))}")
                        
                        if collection == "car_models":
                            context_parts.append(f"  • [{match_type}] {payload.get('brand_name')} {payload.get('name')} {payload.get('year')} - Compatible sizes: {', '.join(payload.get('tyre_sizes', []))}")
                        elif collection == "tyres":
                            context_parts.append(f"  • [{match_type}] {payload.get('brand_name')} {payload.get('model')} - {payload.get('size')} | {payload.get('type')} | £{payload.get('price')} | Stock: {payload.get('stock')}")
                        elif collection == "car_brands":
                            context_parts.append(f"  • [{match_type}] {payload.get('name')} (from {payload.get('country')})")
                        elif collection == "tyre_brands":
                            context_parts.append(f"  • [{match_type}] {payload.get('name')}")
                    else:
                        logger.info(f"[CUSTOMER AGENT]   - Score: {r['score']:.3f} | FILTERED (too low) | {r.get('payload', {}).get('name', r.get('payload', {}).get('model', 'Unknown'))}")

        context = "\n".join(context_parts) if context_parts else "No relevant matches found."

        # Use last 6 messages for context (already built above)
        history_text = "\n".join(context_messages) if context_messages else "First message in this conversation."

        prompt_content = f"""Recent conversation context:
{history_text}

Search results from our database (ranked by relevance):
{context}

Customer's new message: {user_message}

IMPORTANT INSTRUCTIONS:
- Read the conversation context carefully to understand what the customer is referring to
- If they mention "first one", "second one", or similar, look at previous messages to understand what sizes/options were offered
- Use the search results above to provide accurate information
- If you see "Similar match" for car models, suggest them as alternatives
- When customer selects a tyre size, search for and recommend specific tyres in that exact size

Respond following the conversation flow rules. Be natural and helpful!"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt_content),
        ]

        logger.info(f"[CUSTOMER AGENT] Sending prompt to LLM...")
        response = self.llm.invoke(messages)
        logger.info(f"[CUSTOMER AGENT] LLM Response: {response.content[:200]}...")
        logger.info(f"[CUSTOMER AGENT] Extracted info counts: {', '.join([f'{k}: {len(v)}' for k, v in extracted_info.items() if v])}")
        logger.info(f"{'='*80}\n")
        
        return {
            "response": response.content,
            "extracted_info": extracted_info,
            "rag_results": rag_results,
        }
