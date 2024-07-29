from ..db import wrappers

import aiohttp
import asyncio

from configparser import ConfigParser
from os.path import exists
import logging

# create logger and set level
logger = logging.getLogger(__name__)

CONFIG_PATH = 'config.ini'
if not exists(CONFIG_PATH):
    open(CONFIG_PATH, 'w').close() # touch it 

config = ConfigParser()
config.read(CONFIG_PATH)

MAINTAIN_PERIOD = int(config['DEFAULT'].get('MAINTAIN_PERIOD', 60))
DELAY = MAINTAIN_PERIOD/3                                           # NOTE: arbitrary!

async def notify(name):
    print('Handling task', name)
    volunteer = wrappers.task_peek(name)
    link, key = wrappers.r.hmget(f'user:{volunteer}', 'link', 'key')
    if not link:
        logger.warning('User %s has not supplied link', volunteer)
        return
    print('Link', link)
    link = link.rstrip('/') + '/start'
    if link != '/start':
        async with aiohttp.ClientSession() as session:
            logger.info('Making a POST request to %s', link)
            await session.post(link,
                json = {
                    'task': name,
                    'key': key
                }
            )

async def notify_pending():
    print('Watching...')
    for name in wrappers.get_pending():
        try: await notify(name)
        except Exception as e:
            logger.error(e, exc_info=True)
            continue
async def watch_forever():
        while True:
            try:
                await notify_pending()
                await asyncio.sleep(DELAY)
            except KeyboardInterrupt:
                return
            except Exception as e:
                # log it
                logger.error(e, exc_info=True)
                await asyncio.sleep(DELAY)