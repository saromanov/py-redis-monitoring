import redis
import datetime
import threading
import time
from collections import Counter
import hashlib

class Monitoring:
    """
        clearall - clear all store before start monitoring
        monitoring_host, monitoring_port in case if backend is redis
    """
    def __init__(self, host='localhost', port=6379, show_every=10, clearall=False, backend=None, address=None):
        self.servers = []
        self.host = host
        self.port = port
        self.notifications={}
        self.show_every = show_every
        #self.client = redis.ConnectionPool(host=host, port=port)
        self.processing = Processing(host, port)

    def _createClient(self,host, port):
        return redis.ConnectionPool(host=host, port=port)

    def addServer(self, host, port):
        self.servers.append({'host':host, 'port':port})

    def addNotify(self, event, estimatefunc):
        ''' this method provides notification after level
        '''
        self.notifications[event] = estimatefunc

    def _start_receiving(self, connect):
        while True:
            self.processing.receive_response(connect.read_response())

    def _createMonitor(self, server):
        client = self._createClient(server['host'], server['port'])
        connect = client.get_connection('monitor', None)
        connect.send_command('monitor')
        print("monitoring of server {0}:{1} has started...".format(server['host'], server['port']), datetime.datetime.now())
        th = threading.Thread(target=self._start_receiving, args=(connect, ))
        th.setDaemon(True)
        th.start()

    def start(self, addr='localhost'):
        """ Start monitoring """
        self.processing = Processing(self.host, self.port, notify=self.notifications)
        for server in self.servers:
            self._createMonitor(server)
        while True:
            time.sleep(2)

class Processing:
    """ Processing and analytics receive commands """
    def __init__(self, host, port, notify={}):
        self.host = {}
        self.notify = notify
        self.commands_stat = Counter()
        self.redis_store = RedisWrite(host, port)

    def receive_response(self, response):
        if len(response) == 2:
            return

        addr, command, params = self._parse_response(response)
        if command.decode('utf-8') in self.notify:
            self.notify(command)
        command = str(command).lower()
        self.commands_stat[command] += 1
        md5 = hashlib.md5()
        md5.update(addr)
        self.redis_store.putEvent(md5.hexdigest(), command, params)

    def _parse_response(self, response):
        raw = response.split()
        addr = raw[2][:-1]
        command = raw[3][1:-1]
        params = raw[4:]
        return addr, command, params

    def show_commands_stat(self):
        return self.commands_stat


class RedisWrite:
    """ Write data to addition redis db """
    def __init__(self, host, port):
        self.client = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=host, port=port))

    def putEvent(self, addr, command, params):
        """ Increment new command """
        self.client.hincrby(addr, command)
        self.client.hincrby('allhosts', command)
        self.client.hincrby('allhosts:{0}'.format(command), params)
        """Append data by hour """
        hour = datetime.datetime.now().hour
        self.client.hincrby('allhosts:h{0}'.format(hour), command)
        #Append curent received command to list
        self.client.lpush('allhosts:commands', command)

class Event:
    def __init__(self, addr, command, params):
        self.addr = addr
        self.command = command
        self.params = params

