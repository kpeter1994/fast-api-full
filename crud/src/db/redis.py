import redis.asyncio as aioredis
from crud.src.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.from_url(Config.REDIS_URL)

async def add_jti_to_blocklist(token: str) -> None:
    await token_blocklist.set(token,"blocked", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
   jti =  await token_blocklist.get(jti)
   return jti is not None

