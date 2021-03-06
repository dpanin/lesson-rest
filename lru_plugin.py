from aiocache.plugins import BasePlugin
from collections import deque


class LRUPlugin(BasePlugin):
    """
    Implements a Least Recently Used policy with max_keys. The policy does the following:
        - When a key is retrieved get, keys are moved to the beginning of the queue
        - When a key is added (set), keys are added to the beginning of the queue. If
            the queue is full, it will remove as many keys as needed to make space for the new
            ones.
    """

    def __init__(self, max_keys=None):
        super().__init__()
        if max_keys is not None:
            assert max_keys >= 1, "Number of keys must be 1 or bigger"
        self.deque = deque(maxlen=max_keys)

    async def post_get(self, client, key, *args, took=0, **kwargs):
        """
        Remove the key from its current position and set it at the beginning of the queue.
        :param key: string key used in the get operation
        :param client: :class:`aiocache.base.BaseCache` or child instance to use to interact with
            the storage if needed
        """
        if await client.exists(key):
            self.deque.remove(key)
            self.deque.appendleft(key)

    async def post_set(self, client, key, value, *args, took=0, **kwargs):
        """
        Set the given key at the beginning of the queue. If the queue is full, remove the last
        item first.
        :param key: string key used in the set operation
        :param value: obj used in the set operation
        :param client: :class:`aiocache.base.BaseCache` or child instance to use to interact with
            the storage if needed
        """
        if len(self.deque) == self.deque.maxlen:
            await client.delete(self.deque.pop())
        self.deque.appendleft(key)
