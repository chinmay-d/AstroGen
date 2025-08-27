from datetime import timezone
import os
from typing import Any, Dict, Union
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, date as _date, time as _time, timezone
from schemas.astro_schemas import CacheDBEntry

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")


def _bsonify(obj: Any) -> Any:
    """recursively convert python objs to mongo safe"""
    if isinstance(obj, _date) and not isinstance(obj, datetime):
        # store date as datetime at 00:00:00 utc
        return datetime(obj.year, obj.month, obj.day, tzinfo=timezone.utc)
    if isinstance(obj, _time):
        # Mongo has no time type, so store iso
        return obj.strftime("%H:%M:%S")
    if isinstance(obj, dict):
        return {k: _bsonify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_bsonify(v) for v in obj]
    return obj


class AstrogenService:
    @staticmethod
    async def connect_db():
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        return db, client

        
    @staticmethod
    async def add_astro_entry(data: Union[Dict[str, Any], CacheDBEntry]):
        db, client = await AstrogenService.connect_db()
        try:
            entry = data if isinstance(data, CacheDBEntry) else CacheDBEntry.model_validate(data)

            # ensure timestamp is utc
            if entry.timestamp.tzinfo is None:
                entry.timestamp = entry.timestamp.replace(tzinfo=timezone.utc)

            # dump to python types, then normalize to mongo safe
            doc = entry.model_dump(mode="python", exclude_none=True)
            doc = _bsonify(doc)

            result = await db["astro_entries"].insert_one(doc)
            return {"status": "success", "inserted_id": str(result.inserted_id)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            client.close()
