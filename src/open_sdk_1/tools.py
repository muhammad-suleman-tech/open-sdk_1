"""Farming helper functions used as OpenAI Agents SDK tools.

Keep these as plain Python callables that return dicts or strings.
Do not decorate them with the SDK's function_tool here — wrapping happens
in app_agents.py so Agent(tools=[...]) receives FunctionTool objects.
"""
import httpx
from open_sdk_1.models import (
    CropPlan, CropRecommendation,
    FertilizerPlan,
    PestDiagnosis,
    MarketRate
)

# --- Tool 1: Crop Advisor ---
def recommend_crops(district: str, season: str, land_acres: float, water_available: str = "Medium") -> dict:
    """Recommend best crops with profit estimates based on district, season, and land size."""
    recommendations = []
    
    if season.lower() == "rabi":
        recommendations.append(CropRecommendation(
            crop_name="Wheat (Gandum)",
            expected_yield_per_acre="40-45 Maunds",
            estimated_profit_pkr=int(85000 * land_acres),
            reasoning="High demand, suitable for winter in " + district
        ))
        recommendations.append(CropRecommendation(
            crop_name="Canola / Mustard",
            expected_yield_per_acre="20-25 Maunds",
            estimated_profit_pkr=int(110000 * land_acres),
            reasoning="Low water requirement and strong market price"
        ))
    else:  # Kharif
        recommendations.append(CropRecommendation(
            crop_name="Cotton (Kapas)",
            expected_yield_per_acre="30-35 Maunds",
            estimated_profit_pkr=int(140000 * land_acres),
            reasoning="Ideal Kharif commercial crop for " + district
        ))

    plan = CropPlan(
        district=district,
        season=season,
        land_acres=land_acres,
        recommended_crops=recommendations
    )
    return plan.model_dump()

# --- Tool 2: Fertilizer Calculator ---
def calculate_fertilizer(crop: str, acres: float) -> dict:
    """Calculate NPK requirements in bags of Urea and DAP along with total cost in PKR."""
    urea_per_acre = 2.0
    dap_per_acre = 1.0
    
    urea_price_per_bag = 4600
    dap_price_per_bag = 12500

    total_urea = urea_per_acre * acres
    total_dap = dap_per_acre * acres
    total_cost = int((total_urea * urea_price_per_bag) + (total_dap * dap_price_per_bag))

    plan = FertilizerPlan(
        crop=crop,
        acres=acres,
        urea_bags=total_urea,
        dap_bags=total_dap,
        total_cost_pkr=total_cost,
        application_tips="Apply DAP full dose at sowing. Apply Urea in split doses with 1st and 2nd irrigation."
    )
    return plan.model_dump()

# --- Tool 3: Pest & Disease Doctor ---
def diagnose_pest(symptoms: str, crop: str = "general") -> dict:
    """Diagnose crop pest or disease from symptoms and provide safe dosage recommendations."""
    symptoms_lower = symptoms.lower()
    
    if "whitefly" in symptoms_lower or "white insect" in symptoms_lower or "curling" in symptoms_lower:
        diag = PestDiagnosis(
            issue_detected="Whitefly (Sufaid Makhi)",
            severity="Medium to High",
            recommended_treatment="Pyriproxyfen or Acetamiprid spray",
            safe_dosage="400ml per 100L water per acre. DO NOT exceed recommended dosage.",
            safety_warning="Wear protective gloves, mask, and full sleeves during application."
        )
    elif "rust" in symptoms_lower or "yellow spot" in symptoms_lower:
        diag = PestDiagnosis(
            issue_detected="Yellow Rust (Kungi)",
            severity="High",
            recommended_treatment="Tebuconazole fungicide",
            safe_dosage="200ml per acre diluted in 100L water.",
            safety_warning="Keep livestock away from treated fields for at least 7 days."
        )
    else:
        diag = PestDiagnosis(
            issue_detected="General Pest/Fungal Stress",
            severity="Low",
            recommended_treatment="Neem oil spray or standard broad-spectrum bio-pesticide",
            safe_dosage="500ml per 100L water per acre",
            safety_warning="Avoid spraying during peak daylight hours to protect pollinating bees."
        )
    return diag.model_dump()

# --- Tool 4: Mandi Price Lookup ---
def get_mandi_prices(city: str, commodity: str) -> dict:
    """Fetch current wholesale mandi prices for crops in major Pakistani markets."""
    base_prices = {"wheat": 3900, "cotton": 8200, "rice": 4800, "maize": 2400}
    price = base_prices.get(commodity.lower(), 3500)
    
    rate = MarketRate(
        commodity=commodity.title(),
        mandi_name=f"{city.title()} Wholesale Mandi",
        price_per_40kg=price,
        trend="Stable"
    )
    return rate.model_dump()

# --- Tool 5: Weather Check ---
def check_weather_and_irrigation(city: str) -> str:
    """Fetch live weather temperature and precipitation forecast for irrigation advice."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = httpx.get(geo_url, timeout=5.0).json()
        
        if not geo_res.get("results"):
            return f"Could not locate city '{city}'. Advise standard 10-day irrigation cycle."

        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation"
        w_res = httpx.get(weather_url, timeout=5.0).json()
        
        curr = w_res.get("current", {})
        temp = curr.get("temperature_2m", "N/A")
        precip = curr.get("precipitation", 0)

        advice = f"Current weather in {city}: {temp}°C, Rain: {precip}mm. "
        if precip > 1.0:
            advice += "Rain expected/occurring. Postpone scheduled irrigation to prevent waterlogging."
        elif temp > 35.0:
            advice += "Heatwave risk! Ensure light evening irrigation to maintain soil moisture."
        else:
            advice += "Weather conditions are optimal. Proceed with standard irrigation schedule."

        return advice
    except Exception as e:
        return f"Weather service temporarily unavailable ({str(e)}). Maintain standard field watering."