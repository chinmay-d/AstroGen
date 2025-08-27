#### All imports ####
import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from database.astrogen_service import AstrogenService
from schemas.astro_schemas import AstroFAQRequest, AstroInput, CacheDBEntry, LLMSummary
from simple_RAG import run_RAG
from utils import create_return_response, generate_astro_profile, generate_daily_insight, inferZodiac

load_dotenv()

app = FastAPI()

#some initializations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


#### APIs ####
@app.post("/test", description="Test api")
async def test():
    return create_return_response(status_code=200, content="success")


@app.post("/astrogen", description="This api gives your daily astrology insights")
async def astroGen(data: AstroInput):

    # get the zodiac sign
    zodiac = inferZodiac(data.dob)

    # get geo coordinates
    astro_profile, birth_chart_filepath = generate_astro_profile(data)

    llm_data = await generate_daily_insight(astro_profile)
    
    astro_profile.llm_summary = LLMSummary.model_validate(llm_data)

    # save to db
    db_entry = CacheDBEntry(
        zodiac=zodiac,
        birth_chart=str(birth_chart_filepath),
        astro_profile=astro_profile
    )
    save_result = await AstrogenService.add_astro_entry(db_entry)
    if save_result.get("status") == "error":
        raise RuntimeError(f"DB insert failed: {save_result.get('message')}")

    # response
    return create_return_response(status_code=200, content=db_entry.model_dump())


@app.post("/astrofaqs", description="This API is a simple RAG system that can answer your astrology related questions")
async def astrofaqs(req: AstroFAQRequest):
    res = await run_RAG(req.query)
    
    answer = res[0][0].split("\n")[1:]
    return create_return_response(status_code=200, content=answer)