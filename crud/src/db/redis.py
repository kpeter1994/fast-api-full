import aioredis
from crud.src.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
)

async def add_jti_to_blocklist(token: str) -> None:
    await token_blocklist.set(token,"blocked", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
   jti =  await token_blocklist.get(jti)
   return jti is not None

