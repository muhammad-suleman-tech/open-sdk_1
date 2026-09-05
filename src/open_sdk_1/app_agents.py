import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OpenAIChatCompletionsModel,
    function_tool,
    input_guardrail,
)

import open_sdk_1.tools as farm_tools

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY") or "unset",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model_config = OpenAIChatCompletionsModel(model="gemini-3.6-flash", openai_client=client)

# Wrap plain Python functions as SDK FunctionTool objects (not raw callables).
recommend_crops_tool = function_tool(farm_tools.recommend_crops)
calculate_fertilizer_tool = function_tool(farm_tools.calculate_fertilizer)
check_weather_and_irrigation_tool = function_tool(farm_tools.check_weather_and_irrigation)
diagnose_pest_tool = function_tool(farm_tools.diagnose_pest)
get_mandi_prices_tool = function_tool(farm_tools.get_mandi_prices)

OFF_TOPIC_KEYWORDS = ("crypto", "bitcoin", "election", "movie", "football", "sports")


@input_guardrail
def farming_topic_guardrail(context, agent, agent_input):
    """Reject queries that are clearly unrelated to farming or agriculture."""
    text = agent_input if isinstance(agent_input, str) else str(agent_input)
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in OFF_TOPIC_KEYWORDS):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info=(
                "Kisan Dost is strictly dedicated to agricultural assistance "
                "(crops, fertilizers, pests, weather, and market prices). "
                "Please ask a farming-related question."
            ),
        )
    return GuardrailFunctionOutput(tripwire_triggered=False, output_info=None)


# Specialist 1: Agronomy
agronomy_agent = Agent(
    name="Agronomy Specialist",
    instructions="""You are an expert agronomist for Pakistani crops.
Focus on crop selection, soil nutrition, irrigation timing, and fertilizer calculations.
STRICT RULE: Always respond in clear Roman Urdu.""",
    tools=[
        recommend_crops_tool,
        calculate_fertilizer_tool,
        check_weather_and_irrigation_tool,
    ],
    model=model_config,
)

# Specialist 2: Pest Doctor
pest_agent = Agent(
    name="Pest_and_Disease_Doctor",
    instructions="""You are a plant pathologist and pest management expert.
Identify crop diseases from described symptoms, recommend treatments, and strictly enforce safe chemical dosages.
STRICT RULE: Always respond in clear Roman Urdu.""",
    tools=[
        diagnose_pest_tool,
    ],
    model=model_config,
)

# Specialist 3: Market Specialist
market_agent = Agent(
    name="Market_and_Finance_Specialist",
    instructions="""You specialize in agricultural economics and market rates across Pakistani mandis.
Help farmers understand crop wholesale prices. STRICT RULE: Always respond in clear Roman Urdu.""",
    tools=[
        get_mandi_prices_tool,
    ],
    model=model_config,
)

# Main Triage Agent
triage_agent = Agent(
    name="Kisan Dost Triage Agent",
    instructions="""You are Kisan Dost ('Farmer's Friend'), an AI agronomy helpline for Pakistani farmers.
    STRICT RULE: Always respond in clear Roman Urdu.
Analyze the user's request and hand off to the right specialist:
- Hand off to 'Agronomy Specialist' for crop advice, soil health, fertilizer needs, or weather/irrigation.
- Hand off to 'Pest & Disease Doctor' for plant disease symptoms, crop damage, or pesticide treatment.
- Hand off to 'Market & Finance Specialist' for mandi rates and wholesale commodity prices.""",
    handoffs=[agronomy_agent, pest_agent, market_agent],
    input_guardrails=[farming_topic_guardrail],
    model=model_config,
)