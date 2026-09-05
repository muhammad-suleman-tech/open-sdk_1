from typing import List, Optional
from pydantic import BaseModel, Field

# --- 1. Crop Advisor Models ---
class CropRecommendation(BaseModel):
    crop_name: str = Field(description="Name of the recommended crop (e.g., Wheat, Cotton, Maize)")
    expected_yield_per_acre: str = Field(description="Expected yield (e.g., 40 maunds/acre)")
    estimated_profit_pkr: int = Field(description="Estimated net profit per acre in PKR")
    reasoning: str = Field(description="Why this crop is suitable for the given land/season")

class CropPlan(BaseModel):
    district: str
    season: str
    land_acres: float
    recommended_crops: List[CropRecommendation]

# --- 2. Fertilizer Calculator Models ---
class FertilizerPlan(BaseModel):
    crop: str
    acres: float
    urea_bags: float = Field(description="Total 50kg bags of Urea required")
    dap_bags: float = Field(description="Total 50kg bags of DAP required")
    total_cost_pkr: int = Field(description="Total estimated cost in PKR")
    application_tips: str = Field(description="Stage-wise application timing advice")

# --- 3. Pest & Disease Models ---
class PestDiagnosis(BaseModel):
    issue_detected: str = Field(description="Name of pest or disease (e.g., Whitefly, Rust)")
    severity: str = Field(description="Low, Medium, or High")
    recommended_treatment: str = Field(description="Chemical or organic treatment")
    safe_dosage: str = Field(description="STRICT safe dosage instructions per acre")
    safety_warning: str = Field(description="Protective gear and precautions")

# --- 4. Mandi Price Models ---
class MarketRate(BaseModel):
    commodity: str
    mandi_name: str = Field(description="Target mandi/market name (e.g., Multan, Faisalabad)")
    price_per_40kg: int = Field(description="Price in PKR per maund (40 kg)")
    trend: str = Field(description="Price trend: Rising, Stable, or Falling")

# --- 5. Farmer Context / Profile ---
class FarmerProfile(BaseModel):
    district: Optional[str] = None
    land_acres: Optional[float] = None
    current_crop: Optional[str] = None
    season: Optional[str] = "Rabi"  # Default to Rabi or Kharif