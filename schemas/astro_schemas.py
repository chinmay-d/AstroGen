from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime, time, timezone


class AstroInput(BaseModel):
    name: str = Field(..., description="The name of the customer")
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    time_of_birth: time = Field(..., description="Time of birth (HH:MM:SS)")
    city_of_birth: str = Field(..., description="City of birth")
    country_code: Optional[str] = Field(None, description="Your birth country code. example: IN")


# Vedic astrology Panchang
class PanchangData(BaseModel):
    tithi: str = Field(..., description="The lunar day.")
    nakshatra: str = Field(..., description="The lunar mansion or birth star.")
    yoga: str = Field(..., description="A specific luni-solar alignment.")
    karana: str = Field(..., description="Half of a tithi.")
    vaar: str = Field(..., description="The weekday.")

class LLMSummary(BaseModel):
    date: date
    summary: str
    summary_translated_hindi: Optional[str] = None
    advice: List[str]
    advice_translated_hindi: Optional[List[str]] = None
    lucky_window: str
    caution: str
    justification: str

# Thsi holds calculated data
class AstrologicalProfile(AstroInput):
    latitude: float
    longitude: float
    sun_sign: str
    moon_sign: str
    rising_sign: str # Also known as the Ascendant
    panchang: Optional[PanchangData] = None
    llm_summary: Optional[LLMSummary] = None


class AstroFAQRequest(BaseModel):
    query: str


class CacheDBEntry(BaseModel):
    zodiac: str = Field(..., description="Zodiac sign of the custoemr")
    astro_profile: AstrologicalProfile = Field(..., description="Astrological Profile of the user")
    birth_chart: str = Field(..., description="Path of birth chart")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Server-side insertion time in UTC",
    )

