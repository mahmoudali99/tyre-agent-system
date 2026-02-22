import logging
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.config import get_settings
from backend.agents.customer_agent import CustomerAgent
from backend.agents.inventory_agent import InventoryAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.order_agent import OrderAgent
from backend.models.tyre import Tyre
from backend.models.tyre_brand import TyreBrand

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self):
        self.customer_agent = CustomerAgent()
        self.inventory_agent = InventoryAgent()
        self.recommendation_agent = RecommendationAgent()
        self.order_agent = OrderAgent()
        self.classifier = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0,
        )
        self.response_llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )

    async def classify_intent(self, user_message: str, chat_history: list[dict]) -> dict:
        """Use LLM to classify conversation state and extract key info."""
        history_text = "\n".join([
            f"{'Customer' if m.get('sender') == 'user' else 'Agent'}: {m.get('text', '')}"
            for m in (chat_history or [])[-8:]
        ])

        prompt = f"""Analyze this tyre shop conversation and classify the current state.

CONVERSATION:
{history_text}
Customer: {user_message}

Respond ONLY with valid JSON. No markdown, no code blocks, no extra text.
{{
  "state": "greeting|car_identification|size_selection|order_intent|order_placement|order_status|general",
  "car_brand": "brand or null",
  "car_model": "model or null",
  "car_year": "year or null",
  "selected_size": "tyre size like 225/45R17 or null",
  "selected_tyre_brand": "tyre brand if customer chose one or null",
  "selected_tyre_model": "tyre model if customer chose one or null",
  "quantity": null,
  "customer_name": "name or null",
  "wants_order": false
}}

STATE RULES:
- "greeting": First message or general hello
- "car_identification": Customer mentions a car, agent needs to find it and show tyre sizes
- "size_selection": Customer is choosing/has chosen a tyre size from options (e.g. "first one", "1", "225/45R17", "the first size"). IMPORTANT: You MUST extract the actual tyre size value into selected_size by looking at what sizes the agent listed.
- "order_intent": Customer wants to buy/order tyres. Extract tyre details, quantity, and customer name if available. If ALL of (customer_name, selected_tyre_brand, quantity) are known, use "order_placement" instead.
- "order_placement": We have customer_name AND selected_tyre_brand AND quantity - ready to place order.
- "order_status": Customer is asking about order status or tracking. They may provide an order code like MTX-00001. Extract the code into selected_tyre_model field.
- "general": Anything else

CRITICAL: For "size_selection", look at the Agent's previous message to find the actual tyre sizes listed, and map the customer's choice (first/second/1/2) to the correct size string."""

        messages = [
            SystemMessage(content="You are a JSON-only classifier. Output raw JSON only. Never use markdown."),
            HumanMessage(content=prompt),
        ]

        try:
            response = self.classifier.invoke(messages)
            text = response.content.strip()
            if "```" in text:
                text = re.sub(r'```(?:json)?\s*', '', text)
                text = text.replace('```', '').strip()
            result = json.loads(text)
            logger.info(f"[ORCHESTRATOR] Classified: state={result.get('state')}, size={result.get('selected_size')}, "
                       f"tyre={result.get('selected_tyre_brand')}, qty={result.get('quantity')}, name={result.get('customer_name')}")
            return result
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Classification error: {e}")
            return {"state": "general", "wants_order": False}

    async def process(self, user_message: str, chat_history: list[dict], db: AsyncSession) -> dict:
        """Main orchestration: classify → route → respond."""
        logger.info(f"\n{'='*80}")
        logger.info(f"[ORCHESTRATOR] Processing: '{user_message}'")

        # Step 1: Classify intent
        intent = await self.classify_intent(user_message, chat_history)
        state = intent.get("state", "general")
        logger.info(f"[ORCHESTRATOR] State: {state}")

        # Step 2: Route based on state
        if state == "size_selection":
            return await self._handle_size_selection(intent, user_message, chat_history, db)

        elif state == "order_intent":
            return await self._handle_order_intent(intent, user_message, chat_history, db)

        elif state == "order_placement":
            return await self._handle_order_placement(intent, user_message, chat_history, db)

        elif state == "order_status":
            return await self._handle_order_status(intent, user_message, chat_history, db)

        else:
            # greeting, car_identification, general → CustomerAgent
            return await self._handle_customer(user_message, chat_history)

    async def _handle_customer(self, user_message: str, chat_history: list[dict]) -> dict:
        """Default: CustomerAgent handles greeting, car ID, general conversation."""
        logger.info(f"[ORCHESTRATOR] → CustomerAgent")
        result = await self.customer_agent.process_message(user_message, chat_history)
        return {"response": result["response"], "agent": "customer"}

    async def _handle_size_selection(self, intent: dict, user_message: str, chat_history: list[dict], db: AsyncSession) -> dict:
        """Customer picked a size → InventoryAgent (DB) → RecommendationAgent (LLM)."""
        size = intent.get("selected_size")

        if not size:
            logger.warning(f"[ORCHESTRATOR] No size extracted, falling back to CustomerAgent")
            return await self._handle_customer(user_message, chat_history)

        # InventoryAgent: get REAL stock from PostgreSQL
        logger.info(f"[ORCHESTRATOR] → InventoryAgent: checking DB for size '{size}'")
        inventory = await self.inventory_agent.check_stock_by_size(db, size)
        logger.info(f"[ORCHESTRATOR] ← InventoryAgent: {len(inventory)} tyres in stock")

        for t in inventory:
            logger.info(f"[ORCHESTRATOR]   • {t['brand']} {t['model']} - £{t['price']} | Stock: {t['stock']}")

        if not inventory:
            return {
                "response": f"I'm sorry, we don't currently have any tyres in stock for size **{size}**. Would you like to check a different size?",
                "agent": "inventory",
            }

        # RecommendationAgent: rank and recommend
        car_info = {
            "brand": intent.get("car_brand", "Unknown"),
            "model": intent.get("car_model", "Unknown"),
            "year": intent.get("car_year", "Unknown"),
            "size": size,
        }

        logger.info(f"[ORCHESTRATOR] → RecommendationAgent: ranking {len(inventory)} tyres")
        recommendation = await self.recommendation_agent.recommend(car_info, inventory)
        logger.info(f"[ORCHESTRATOR] ← RecommendationAgent: done")

        return {"response": recommendation, "agent": "recommendation"}

    async def _handle_order_intent(self, intent: dict, user_message: str, chat_history: list[dict], db: AsyncSession) -> dict:
        """Customer wants to order but may be missing details."""
        customer_name = intent.get("customer_name")
        selected_tyre_brand = intent.get("selected_tyre_brand")
        quantity = intent.get("quantity")

        logger.info(f"[ORCHESTRATOR] Order intent - name: {customer_name}, tyre: {selected_tyre_brand}, qty: {quantity}")

        # If we have everything, go straight to placement
        if customer_name and selected_tyre_brand and quantity:
            return await self._handle_order_placement(intent, user_message, chat_history, db)

        # Otherwise, ask for missing details
        missing = []
        if not customer_name:
            missing.append("your full name")
        if not quantity:
            missing.append("how many tyres you need")

        # Generate a response asking for missing details
        history_text = "\n".join([
            f"{'Customer' if m.get('sender') == 'user' else 'Agent'}: {m.get('text', '')}"
            for m in (chat_history or [])[-6:]
        ])

        ask_prompt = f"""You are a friendly tyre specialist at Matrax Tyres. The customer wants to place an order.

Conversation:
{history_text}
Customer: {user_message}

Known details:
- Customer name: {customer_name or 'NOT PROVIDED'}
- Selected tyre: {selected_tyre_brand or 'NOT SPECIFIED'} {intent.get('selected_tyre_model', '') or ''}
- Quantity: {quantity or 'NOT SPECIFIED'}
- Tyre size: {intent.get('selected_size') or 'NOT SPECIFIED'}

We still need: {', '.join(missing) if missing else 'confirmation to proceed'}.

Write a SHORT, friendly message asking for the missing details. If we have the tyre but not the name/quantity, ask for those.
Keep it to 2-3 sentences max. Use emojis sparingly."""

        messages = [
            SystemMessage(content="You are a friendly tyre shop assistant. Be brief and warm."),
            HumanMessage(content=ask_prompt),
        ]
        response = self.response_llm.invoke(messages)
        return {"response": response.content, "agent": "customer"}

    async def _handle_order_status(self, intent: dict, user_message: str, chat_history: list[dict], db: AsyncSession) -> dict:
        """Customer is asking about order status."""
        import re as _re
        # Try to extract order code from the message or conversation
        code_match = _re.search(r'(?:MTX|mts|MTS|mtx)[\-\s]?(\d+)', user_message)
        if not code_match:
            # Search in recent history
            for m in reversed(chat_history or []):
                code_match = _re.search(r'(?:MTX|mts|MTS|mtx)[\-\s]?(\d+)', m.get('text', ''))
                if code_match:
                    break

        if not code_match:
            return {
                "response": "Could you please provide your order code? It looks like **MTX-XXXXX** (e.g. MTX-00001). 😊",
                "agent": "order",
            }

        order_id = int(code_match.group(1))
        order_code = f"MTX-{order_id:05d}"
        logger.info(f"[ORCHESTRATOR] → OrderAgent: looking up order {order_code}")

        order_data = await self.order_agent.get_order(db, order_id)
        if not order_data:
            return {
                "response": f"I couldn't find an order with code **{order_code}**. Please double-check the code and try again.",
                "agent": "order",
            }

        status = order_data['status']
        items_text = "\n".join([
            f"  • {item['tyre']} x{item['quantity']} — £{item['unit_price'] * item['quantity']:.2f}"
            for item in order_data['items']
        ])

        # Status-based next steps
        next_steps = {
            "Pending": "Your order is being reviewed. We'll start preparing it shortly.",
            "Confirmed": "Your order has been confirmed and is being prepared.",
            "Processing": "Your tyres are being prepared for collection/delivery.",
            "Ready": "Your tyres are ready! You can collect them from our workshop.",
            "Shipped": "Your order has been shipped and is on its way to you.",
            "Delivered": "Your order has been delivered. We hope you're happy with your tyres!",
            "Completed": "Your order is complete. Thank you for shopping with us!",
            "Cancelled": "This order has been cancelled. Please contact us if you have questions.",
        }
        next_step = next_steps.get(status, "Please contact us for more details.")

        response = (
            f"📋 **Order Status: {order_code}**\n\n"
            f"• **Status:** {status}\n"
            f"• **Customer:** {order_data['customer_name']}\n"
            f"• **Items:**\n{items_text}\n"
            f"• **Total:** £{order_data['total_amount']:.2f}\n\n"
            f"**Next steps:** {next_step}\n\n"
            f"Is there anything else I can help you with? 😊"
        )
        return {"response": response, "agent": "order"}

    async def _handle_order_placement(self, intent: dict, user_message: str, chat_history: list[dict], db: AsyncSession) -> dict:
        """Place the actual order in the database."""
        customer_name = intent.get("customer_name")
        selected_tyre_brand = intent.get("selected_tyre_brand")
        selected_tyre_model = intent.get("selected_tyre_model")
        quantity = intent.get("quantity", 4)
        selected_size = intent.get("selected_size")

        logger.info(f"[ORCHESTRATOR] → OrderAgent: placing order")
        logger.info(f"[ORCHESTRATOR]   Customer: {customer_name}")
        logger.info(f"[ORCHESTRATOR]   Tyre: {selected_tyre_brand} {selected_tyre_model}")
        logger.info(f"[ORCHESTRATOR]   Qty: {quantity}, Size: {selected_size}")

        if not customer_name or not selected_tyre_brand:
            # Missing critical info
            return await self._handle_order_intent(intent, user_message, chat_history, db)

        # Find the tyre in DB
        try:
            query = (
                select(Tyre, TyreBrand.name.label("brand_name"))
                .join(TyreBrand, Tyre.brand_id == TyreBrand.id)
                .where(TyreBrand.name.ilike(f"%{selected_tyre_brand}%"))
            )
            if selected_tyre_model:
                query = query.where(Tyre.model.ilike(f"%{selected_tyre_model}%"))
            if selected_size:
                query = query.where(Tyre.size == selected_size)

            result = await db.execute(query)
            row = result.first()

            if not row:
                logger.warning(f"[ORCHESTRATOR] Tyre not found in DB: {selected_tyre_brand} {selected_tyre_model}")
                return {
                    "response": f"I couldn't find **{selected_tyre_brand} {selected_tyre_model or ''}** in our system. Could you double-check the tyre you'd like to order?",
                    "agent": "order",
                }

            tyre, brand_name = row

            # Check stock
            if tyre.stock < quantity:
                return {
                    "response": f"Sorry, we only have **{tyre.stock}** units of {brand_name} {tyre.model} in stock, but you need {quantity}. Would you like to order {tyre.stock} instead, or choose a different tyre?",
                    "agent": "order",
                }

            # Place order via OrderAgent
            order_result = await self.order_agent.create_order(
                db=db,
                customer_name=customer_name,
                items=[{"tyre_id": tyre.id, "quantity": quantity}],
            )

            if order_result["success"]:
                order_code = f"MTX-{order_result['order_id']:05d}"
                total = order_result["total_amount"]
                logger.info(f"[ORCHESTRATOR] ← OrderAgent: ✅ Order placed! Code: {order_code}, Total: £{total:.2f}")

                response = (
                    f"🎉 **Order Confirmed!**\n\n"
                    f"• **Order Code:** `{order_code}`\n"
                    f"• **Status:** Pending\n"
                    f"• **Customer:** {customer_name}\n"
                    f"• **Tyre:** {brand_name} {tyre.model} ({tyre.size})\n"
                    f"• **Quantity:** {quantity}\n"
                    f"• **Unit Price:** £{tyre.price:.2f}\n"
                    f"• **Total:** £{total:.2f}\n\n"
                    f"Thank you for shopping with Matrax Tyres! 😊\n"
                    f"Please quote your order code **{order_code}** when collecting your tyres.\n"
                    f"You can check your order status anytime by providing your order code."
                )
                return {"response": response, "agent": "order", "order_code": order_code}
            else:
                logger.error(f"[ORCHESTRATOR] ← OrderAgent: ❌ {order_result['message']}")
                return {
                    "response": f"Sorry, there was an issue placing your order: {order_result['message']}",
                    "agent": "order",
                }

        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Order error: {e}", exc_info=True)
            return {
                "response": "I'm sorry, there was an error processing your order. Please try again.",
                "agent": "order",
            }
