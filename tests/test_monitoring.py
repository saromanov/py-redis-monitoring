import redismonitor
import pytest


@pytest.mark.incremental
class TestMonitoring:
    mon = redismonitor.Monitoring()

    def test_init(self):
        assert self.mon.host == 'localhost'
        assert self.mon.port == 6379

    def test_add_server(self):
        self.mon.addServer('localhost', '6379')
        self.mon.addServer('localhost', '6380')
        self.mon.addServer('localhost', '6381')
        self.mon.addServer('localhost', '6382')
        assert len(self.mon.servers) == 4

    def test_add_notofy(self):
        self.mon.addNotify('hset', lambda x: x)
        assert len(self.mon.notifications) == 1
