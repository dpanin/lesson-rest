import aiohttp
from aiohttp import web
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from lru_plugin import LRUPlugin


# Set caching time to 10 minutes and use MemoryCache with LRU policy 
# to store cache as pickled objects
@cached(
    ttl=600,
    key_from_attr="lesson_id",
    cache=SimpleMemoryCache,
    plugins=[LRUPlugin(max_keys=100)],
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

    return resp.status, json_response['lessons'][0]['steps']


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
