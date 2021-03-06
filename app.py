from datetime import datetime
from time import mktime

import aiohttp
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from aiohttp import web
from lru_plugin import LRUPlugin

steps_cache = SimpleMemoryCache(serializer=PickleSerializer(), plugins=[LRUPlugin(max_keys=1000)])


class HTTPForbidden(Exception):
    pass


async def get_steps(lesson_id, lsteps, update_date):
    """Works with the cache, where steps are stored.

    Return True if step is theoretical and False if not. If access if forbidden, raise HTTPForbidden error.

    :param lesson_id: str lesson id
    :param lsteps: list of lesson's steps
    :param update_date: int timestamp when lesson was updated
    """
    result = []
    if await steps_cache.exists(lesson_id):
        cached_steps = await steps_cache.get(lesson_id)
        # If data wasn't updated before, then return from cache
        if cached_steps[0] >= update_date:
            if cached_steps[1] == 'Forbidden':
                raise HTTPForbidden
            return cached_steps[1]
    # If cache doesn't exist or not valid, then update it
    for step_id in lsteps:
        async with aiohttp.request(
                'GET', 'https://stepik.org/api/steps/{}'.format(step_id)) as resp:
            # Raise error if can't get access to step
            if resp.status == 403:
                await steps_cache.set(lesson_id, (None, 'Forbidden'))
                raise HTTPForbidden
            json_response = await resp.json()
            # Check if step is theoretical
            if json_response['steps'][0]['block']['name'] == 'text':
                result.append(step_id)
            else:
                pass
    await steps_cache.set(lesson_id, (update_date, result))
    return result


# Caches Stepik /api/lessons response for 2 minutes and use MemoryCache
# with LRU policy to store cache as pickled objects
@cached(
    ttl=120,
    key_from_attr="lesson_id",
    cache=SimpleMemoryCache,
    plugins=[LRUPlugin(max_keys=1000)],
    serializer=PickleSerializer())
async def get_lesson(lesson_id):
    """Make request to Stepik REST API and process a response.
    :param lesson_id: string number used to get steps for lesson with the same id
    """
    async with aiohttp.request(
            'GET', 'https://stepik.org/api/lessons/{}'.format(lesson_id)) as resp:
        # Return status code if bad response from Stepik server
        if not resp.status == 200:
            return resp.status, None
        json_response = await resp.json()
    # Convert time string to timestamp
    update_date = int(
        mktime(datetime.strptime(json_response['lessons'][0]['update_date'], "%Y-%m-%dT%H:%M:%SZ").timetuple()))
    try:
        results = await get_steps(lesson_id, json_response['lessons'][0]['steps'], update_date)
    except HTTPForbidden:
        return 403, []
    return resp.status, results


async def lesson(request):
    """Main resource which processes requests."""
    lesson_id = request.match_info.get("lesson_id", "Anonymous")
    # Check for valid lesson id
    if not lesson_id.isdigit():
        return aiohttp.web.Response(status=400, body="Invalid lesson_id.")
    # Get json or status code, which will be included in respone
    status, body = await get_lesson(lesson_id)
    # Return status code if received bad response from Stepik server
    if status != 200:
        return aiohttp.web.Response(status=status)
    return aiohttp.web.json_response(body)


app = web.Application()
app.router.add_get('/lesson={lesson_id}', lesson)  # Create route

# Run aiohttp server
web.run_app(app, host='127.0.0.1', port=8080)
