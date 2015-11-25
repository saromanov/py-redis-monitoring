import redis
import datetime
import time
from collections import Counter
import hashlib
import asyncio


class Monitoring:

    """
        clearall - clear all store before start monitoring
        monitoring_host, monitoring_port in case if backend is redis
    """

    def __init__(self, host='localhost', port=6379, show_every=10, clearall=False, backend=None, address=None):
        self.servers = []
        self.host = host
        self.port = port
        self.notifications = {}
        self.show_every = show_every
        self.processing = Processing(host, port)

    def _createClient(self, host, port):
        return redis.ConnectionPool(host=host, port=port)

    def addServer(self, host, port):
        ports = self._processPort(port)
        for p in ports:
            self.servers.append({'host': host, 'port': p})

    def _processPort(self, port):
        ''' In the case if port is 638[1,2]
        '''
        idx = port.find('[')
        if idx == -1:
            return [port]
        idxend = port.find(']')
        if idxend == -1:
            raise Exception("Error in port")
        starts = port[:idx]
        ports = port[idx + 1:idxend]
        return [starts + p for p in ports.split(',')]

    def addNotify(self, event, estimatefunc):
        ''' this method provides notification if estimatefunc is true
        '''
        self.notifications[event] = estimatefunc

    def _start_receiving(self, connect):
        while True:
            self.processing.receive_response(connect.read_response())

    async def _createMonitor(self, server):
        client = self._createClient(server['host'], server['port'])
        connect = client.get_connection('monitor', None)
        connect.send_command('monitor')
        self._start_receiving(connect)

    async def _start(self, addr='localhost'):
        """ Start monitoring """
        self.processing = Processing(
            self.host, self.port, notify=self.notifications)
        print("Monitoring of servers: ")
        for server in self.servers:
            print("{0}:{1} has been started...".format(
                server['host'], server['port']), datetime.datetime.now())
            await self._createMonitor(server)
        while True:
            time.sleep(2)

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._start())
        loop.close()


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
        print(addr)
        command = command.decode('utf-8')
        command = command.lower()
        self.commands_stat[command] += 1
        md5 = hashlib.md5()
        md5.update(addr)
        self.redis_store.putEvent(md5.hexdigest(), command, params)

    def _parse_response(self, response):
        '''
          This method returns triplet of address of getting command, command
          and additional params
        '''
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
        self.client = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(host=host, port=port))

    def putEvent(self, addr, command, params):
        """ Increment new command """
        self.client.hincrby(addr, command)
        self.client.hincrby('allhosts', command)
        self.client.hincrby('allhosts:{0}'.format(command), params)
        self.client.hincrby('monitor_{0}'.format(addr), command)
        """Append data by hour """
        hour = datetime.datetime.now().hour
        self.client.hincrby('allhosts:h{0}'.format(hour), command)
        # Append curent received command to list
        self.client.lpush('allhosts:commands', command)


class Event:

    def __init__(self, addr, command, params):
        self.addr = addr
        self.command = command
        self.params = params
