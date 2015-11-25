import redis


class BackendRedis:

    """ Note: This client don't need to send information to processing """

    def __init__(self, addr, port):
        self.client = redis.ConnectionPool(host=host, port=port)
