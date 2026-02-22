import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from backend.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RecommendationAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
        self.system_prompt = """You are a tyre recommendation specialist at Matrax Tyres.

YOUR TASK: Given a car and available tyres from our inventory, recommend the BEST tyre as your top pick and list the alternatives.

RESPONSE FORMAT (follow this exactly):
1. Start with a warm one-liner about the car
2. Show your **⭐ Top Recommendation** with reasoning (1-2 sentences why)
3. Show **Other Options** as a compact list
4. Ask if they'd like to order

FORMATTING RULES:
- Use bullet points (•) not asterisks
- Show prices with £ symbol
- Keep it SHORT (no walls of text)
- NEVER mention tyre IDs or database details
- NEVER mention stock levels or how many units are available
- Add emojis sparingly (🚗 ⭐ 💰 ✅)

EXAMPLE:
Great choice for your BMW 320i 2023! Here are the available tyres in 225/45R17:

⭐ **Top Pick: Michelin Pilot Sport 4** - £189.99
Performance tyre with excellent grip and handling. Perfect for your BMW!

**Other options:**
• **Bridgestone Turanza T005** - £165.99 | Comfort
• **Toyo Celsius II** - £149.99 | All-Season

Would you like to order any of these? Just let me know which one and how many! 😊"""

    async def recommend(self, car_info: dict, available_tyres: list[dict]) -> str:
        logger.info(f"[RECOMMENDATION AGENT] Generating recommendation for {len(available_tyres)} tyres")

        tyres_text = "\n".join([
            f"- {t.get('brand', t.get('brand_name', ''))} {t.get('model', '')} | "
            f"Size: {t.get('size', '')} | Type: {t.get('type', '')} | "
            f"Price: £{t.get('price', 0):.2f}"
            for t in available_tyres
        ])

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Car: {car_info.get('brand', 'Unknown')} {car_info.get('model', 'Unknown')} {car_info.get('year', '')}
Selected size: {car_info.get('size', 'Unknown')}

Available tyres from our inventory:
{tyres_text}

Recommend the best tyre and list alternatives. Keep it concise!"""),
        ]

        response = self.llm.invoke(messages)
        logger.info(f"[RECOMMENDATION AGENT] Response generated: {response.content[:100]}...")
        return response.content
