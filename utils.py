import asyncio
from datetime import datetime
import json
import logging
import os
from typing import List
import uuid
from zoneinfo import ZoneInfo
from openai import AsyncOpenAI
from geopy.geocoders import Nominatim
from kerykeion import AstrologicalSubject, KerykeionChartSVG
import os, uuid, shutil
from pathlib import Path
from dotenv import load_dotenv
from model_inference import translate
from schemas.astro_schemas import AstroInput, AstrologicalProfile, PanchangData

#### Some initializations ####
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_DIR = os.getenv("DATA_DIR")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


SIGNS_FULL = {
    "Ari":"Aries","Tau":"Taurus","Gem":"Gemini","Can":"Cancer","Leo":"Leo","Vir":"Virgo",
    "Lib":"Libra","Sco":"Scorpio","Sag":"Sagittarius","Cap":"Capricorn","Aqu":"Aquarius","Pis":"Pisces"
}
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashirsha","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
    "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
TITHIS = [
    "Shukla Pratipada","Shukla Dwitiya","Shukla Tritiya","Shukla Chaturthi","Shukla Panchami",
    "Shukla Shashthi","Shukla Saptami","Shukla Ashtami","Shukla Navami","Shukla Dashami",
    "Shukla Ekadashi","Shukla Dwadashi","Shukla Trayodashi","Shukla Chaturdashi","Purnima",
    "Krishna Pratipada","Krishna Dwitiya","Krishna Tritiya","Krishna Chaturthi","Krishna Panchami",
    "Krishna Shashthi","Krishna Saptami","Krishna Ashtami","Krishna Navami","Krishna Dashami",
    "Krishna Ekadashi","Krishna Dwadashi","Krishna Trayodashi","Krishna Chaturdashi","Amavasya"
]
YOGAS = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti","Shoola",
    "Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyana",
    "Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
MOVABLE_KARANAS = ["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti"]


#### utility functions ####
def create_return_response(status_code, content):
    return {"status_code": status_code, "content": content}


def inferZodiac(date_to_check: datetime) -> str:
    """Return the zodiac sign for the given datetime of birth."""
    day = date_to_check.day
    month = date_to_check.month

    if month == 1:
        # January: Capricorn or Aquarius
        return "Capricorn" if day < 20 else "Aquarius"
    elif month == 2:
        # February: Aquarius or Pisces
        return "Aquarius" if day < 19 else "Pisces"
    elif month == 3:
        # March: Pisces or Aries
        return "Pisces" if day < 21 else "Aries"
    elif month == 4:
        # April: Aries or Taurus
        return "Aries" if day < 20 else "Taurus"
    elif month == 5:
        # May: Taurus or Gemini
        return "Taurus" if day < 21 else "Gemini"
    elif month == 6:
        # June: Gemini or Cancer
        return "Gemini" if day < 21 else "Cancer"
    elif month == 7:
        # July: Cancer or Leo
        return "Cancer" if day < 23 else "Leo"
    elif month == 8:
        # August: Leo or Virgo
        return "Leo" if day < 23 else "Virgo"
    elif month == 9:
        # September: Virgo or Libra
        return "Virgo" if day < 23 else "Libra"
    elif month == 10:
        # October: Libra or Scorpio
        return "Libra" if day < 23 else "Scorpio"
    elif month == 11:
        # November: Scorpio or Sagittarius
        return "Scorpio" if day < 22 else "Sagittarius"
    elif month == 12:
        # December: Sagittarius or Capricorn
        return "Sagittarius" if day < 22 else "Capricorn"
    else:
        return "Invalid month"
    

async def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-4o-mini", temperature=0, response_format={"type": "json_object"}, max_completion_tokens: int = 2048):
    try:
        # Make the API request
        params = {
            "model": model,
            "messages": messages,
            "response_format": response_format,
            "max_completion_tokens": max_completion_tokens
        }
        # only include temperature if model supports it
        if model not in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            params["temperature"] = temperature

        response = await openai_client.beta.chat.completions.parse(**params)
    
        return {"status": "success", "response": json.loads(response.choices[0].message.content)}

    except Exception as e:
        # log the error and return an error response
        return {"status": "error", "response": str(e)}
    

def get_coordinates(location_string: str) -> tuple[float, float]:
    """Converts a location string to latitude and longitude."""
    geolocator = Nominatim(user_agent="astro_insights_app")
    try:
        location = geolocator.geocode(location_string)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        logging.info(f"Error geocoding {location_string}: {e}")
    raise ValueError("Could not find coordinates for the specified location.")


def get_timezone_str(dt_obj: datetime, default_tz: str = "Asia/Kolkata") -> str:
    """
    Extracts the timezone string from a datetime object.
    else returns the provided default timezone string.
    """
    if dt_obj.tzinfo is not None and hasattr(dt_obj.tzinfo, 'key'):
        # timezone objects using the standard zoneinfo
        return dt_obj.tzinfo.key
    else:
        # for bjects or objects with non standard tzinfo
        return default_tz


def to_full_sign(abbr: str) -> str:
    return SIGNS_FULL.get(abbr, abbr)


def compute_panchanga(sun_long: float, moon_long: float, dt_local: datetime):
    """All angles in degrees, sidereal; dt_local is local birth datetime."""
    delta = (moon_long - sun_long) % 360.0
    # Tithi (12° per tithi)
    tithi_idx = int(delta // 12) + 1  # 1..30
    tithi_name = TITHIS[tithi_idx - 1]
    # Yoga (sum, 27 parts)
    yoga_long = (moon_long + sun_long) % 360.0
    yoga_idx = int(yoga_long // (360.0 / 27)) + 1  # 1..27
    yoga_name = YOGAS[yoga_idx - 1]
    # Nakshatra (Moon longitude in 27 parts)
    nak_idx = int(moon_long // (360.0 / 27))  # 0..26
    nak_name = NAKSHATRAS[nak_idx]
    # Karana (6° per karana; map 1..60 to names)
    karana_serial = int(delta // 6) + 1  # 1..60
    if karana_serial == 1:
        karana_name = "Kimstughna"
    elif 2 <= karana_serial <= 57:
        karana_name = MOVABLE_KARANAS[(karana_serial - 2) % 7]
    elif karana_serial == 58:
        karana_name = "Shakuni"
    elif karana_serial == 59:
        karana_name = "Chatushpada"
    else:
        karana_name = "Naga"
    # Weekday
    vaar = dt_local.strftime("%A")
    return {
        "tithi": tithi_name,
        "nakshatra": nak_name,
        "yoga": yoga_name,
        "karana": karana_name,
        "vaar": vaar,
    }


def save_svg_with_uuid(subject) -> Path:
    """The idea behind this func is to save the svg file in a temp dir as keryeion does't allow us
    to save the file according to our naming convention. So we save it in a temp dir and create a 
    unique uuid filename and then use this svg file and rename and move it to our data directory.
    """
    data_dir = Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    # create a temp dir to save
    tmp_dir = data_dir / f".kr_tmp_{uuid.uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # create a kerykerion svg obj
    chart = KerykeionChartSVG(subject, new_output_directory=str(tmp_dir))
    chart.makeSVG()  #this will write svg inthe dir

    # get all the svg files and select the newest
    svg_files = list(tmp_dir.glob("*.svg"))
    if not svg_files:
        # then nothing is produced so we remove tmporary dir created
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise FileNotFoundError("Kerykeion did not produce any SVG in the temp directory.")

    # the newest file is the latest so get it
    src = max(svg_files, key=lambda p: p.stat().st_mtime)

    # move and rename to final UUID name
    dest = data_dir / f"{uuid.uuid4()}.svg"
    src.replace(dest)

    # clean tmp dir
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return dest


def generate_astro_profile(input_data: AstroInput, use_sidereal: bool = True, sidereal_mode: str = "LAHIRI") -> AstrologicalProfile:
    """
    Build an astro profile using Kerykeion v4.
    - If latitude/longitude/timezone_str are provided, Kerykeion skips GeoNames.
    - Otherwise it will resolve city+country (may hit GeoNames limits).
    """
    dt_local = datetime.combine(input_data.dob, input_data.time_of_birth)
    
    #get latitude and longitude
    latitude, longitude = get_coordinates(input_data.city_of_birth)
    timezone_str = get_timezone_str(dt_local) # if timezone str is not present by default we take the Indian timezone

    subject = AstrologicalSubject( #this will get use astrological subject
        input_data.name,
        dt_local.year, dt_local.month, dt_local.day, dt_local.hour, dt_local.minute,
        lat=latitude, lng=longitude, tz_str=timezone_str,
        city=input_data.city_of_birth, nation=input_data.country_code or "IN",
        zodiac_type=("Sidereal" if use_sidereal else "Tropic"),
        sidereal_mode=(sidereal_mode if use_sidereal else None),
    )

    ### create birth chart if required ###
    filepath = save_svg_with_uuid(subject)
    logging.info(f"SVG saved to: {filepath}")

    # get the 3 important signs
    sun_sign = to_full_sign(subject.sun["sign"])
    moon_sign = to_full_sign(subject.moon["sign"])
    rising_sign = to_full_sign(subject.first_house["sign"])  # ascendant/rising

    # panchang computed
    sun_long = subject.sun["abs_pos"]
    moon_long = subject.moon["abs_pos"]
    p = compute_panchanga(sun_long, moon_long, dt_local)
    panchang = PanchangData(**p)

    return AstrologicalProfile(
        name=input_data.name,
        dob=input_data.dob,
        time_of_birth=input_data.time_of_birth,
        city_of_birth=input_data.city_of_birth,
        latitude=latitude,
        longitude=longitude,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        rising_sign=rising_sign,
        panchang=panchang,
    ), filepath


async def generate_daily_insight(data: AstrologicalProfile):
    today_str = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()

    system_msg = {
        "role": "system",
        "content": (
            "You are an expert astrologer. Return STRICT JSON only.\n"
            "Schema:\n"
            "{\n"
            '  "date": "YYYY-MM-DD",\n'
            '  "summary": "1–2 lines daily theme",\n'
            '  "advice": ["short actionable tip", "..."],\n'
            '  "lucky_window": "local time range e.g. 14:00–16:00",\n'
            '  "caution": "one concise risk to watch",\n'
            '  "justification": "brief rationale referencing sun/moon/rising or panchang"\n'
            "}\n"
        ),
    }

    user_msg = {
        "role": "user",
        "content": (
            "Generate today's daily insight for the following astrological profile. "
            "Use the provided local date. Keep output compact and helpful.\n\n"
            f"date: {today_str}\n"
            f"profile: {data.model_dump() if hasattr(data, 'model_dump') else data}"
        ),
    }

    resp = await chat_completion_request(
        messages=[system_msg, user_msg],
        model="gpt-5-mini",
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    if resp.get("status") == "error":
        raise RuntimeError(f"Error occured when generating daily insight: {resp.get('response')}")

    #translate to hindi async
    llm_data = resp.get("response")
    llm_data["summary_translated_hindi"] = await translate(llm_data.get("summary"), src_lang="eng_Latn", tgt_lang="hin_Deva")
    
    translation_tasks = list()
    for advice in llm_data.get("advice"):
        translation_tasks.append(translate(advice, src_lang="eng_Latn", tgt_lang="hin_Deva"))

    translated_advice = await asyncio.gather(*translation_tasks)
    llm_data["advice_translated_hindi"] = translated_advice

    #return the llm_summary
    return llm_data




