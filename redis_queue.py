from config import config
import redis


class RedisQueue(object):
    """Simple Queue with Redis Backend"""

    def __init__(self, name, namespace='queue'):
        """
        The default connection parameters are:
        host='localhost',
        port=6379,
        db=0
        """
        redis_kwargs = {
            "host": config["redis"]["redis_host"],
            "port": config["redis"]["redis_port"],
            "db": config["redis"]["redis_db"]
        }

        self.__db = redis.Redis(**redis_kwargs)
        self.key = '{}:{}'.format(namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize()

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.
        If optional args block is true
        and timeout is None (the default), block
        if necessary until an item is available.
        """
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def purge(self):
        self.__db.delete(self.key)

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)
