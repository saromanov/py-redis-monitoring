import redismonitor
import redis
import time


class TestClient:
    cli = redismonitor.ProcessingClient()
    rediscli = redis.StrictRedis(host='localhost', port=6380)

    def test_commands_stat1(self):
        self.cli.removeData()
        self.rediscli.set('foo', 'bar')
        self.rediscli.set('bar', 'foo')
        time.sleep(1)
        commands = self.cli.getCommandsStat()
        assert len(commands) == 1
        assert commands[0][0] == 'set'
        assert commands[0][1] == 2

    def test_commands_stat(self):
        self.cli.removeData()
        self.rediscli.set('foo', 'bar')
        self.rediscli.lpush('doom', '2')
        self.rediscli.set('loop', 'noop')
        time.sleep(1)
        commands = self.cli.getCommandsStat()
        assert len(commands) == 2
