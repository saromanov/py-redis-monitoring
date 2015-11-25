import redismonitor
import redis


class TestClient:
    cli = redismonitor.ProcessingClient()  # Client initialization
    rediscli = redis.StrictRedis(host='localhost', port=6380, db=0)

    def test_first(self):
        self.rediscli.set('foo', 'bar')
        self.rediscli.set('foo', 'bar2')
        commands = self.cli.getCommandsStat()
        assert len(commands) == 1
        assert commands[0][0] == 'set'
        assert commands[0][1] == '2'
