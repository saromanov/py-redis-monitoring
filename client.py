import redis
import hashlib
from functools import reduce

class ProcessingClient:
    """ Client just connect to another redis db """
    def __init__(self, backend='redis', host='localhost', port=6379):
        if backend == 'redis':
            self.client = redis.Redis(connection_pool=redis.ConnectionPool(host=host, port=str(6379)))

    def _processHost(self, host):
        md5 = hashlib.md5()
        md5.update(host)
        return 'monitor_{0}'.format(md5.hexdigest())

    def getCommandStat(self, command, host='allhosts'):
        if host != 'allhosts':
            host = 'monitor_{0}'.format(host)
        return int(self.client.hget(host, command))

    def getCommandStatByHour(self, hour, command, host='allhosts'):
        """ Return statistics for commands by hour.
            For example, hour=10 command='hset' return statistic for command in 10 a.m
        """
        if hour >=0 and hour <= 23:
            return self.client.hget('{0}:h{1}'.format(host, hour), command)
        raise Exception("Error in hour param")

    def getCommandsStat(self, host='allhosts'):
        """ Return counters for all commands """
        if host != 'allhosts':
            host = self._processHost(host)
        def sortResults(results):
            return sorted(results, key=lambda x: x[1], reverse=True)
        result = list(map(lambda x: (x.decode('utf-8'), self.getCommandStat(x, host=host)), self.client.hkeys(host)))
        return sortResults(result)

    def getCommandsParams(self, command, host='allhosts'):
        if host != 'allhosts':
            host = self._processHost(host)
        return self.client.hkeys('{0}:{1}'.format(host, command))

    def getAllCommandsHistory(self, host='allhosts'):
        """ Return history for all commands """
        if host != 'allhosts':
            host = self._processHost(host)
        return self.client.lrange('{0}:commands'.format(host), 0, -1)

    def getDBSize(self):
        script = """
        local result = redis.call("dbsize")
        return tonumber(result), 10
        """
        value = self.client.register_script(script)
        return value()

    def getCommandsDistribution(self):
        ''' This method return distribution of received commands
            For example, if we have a 20 commands hset and 20 commands hget,
            getCommandsDistribution will returns (('hset', 0.5), (hget, 0.5))
        '''
        commands = self.getCommandsStat()
        if len(commands) == 0:
            raise Exception("Commands stat is not found")
        totalnum = reduce(lambda x,y: x + y[1], commands, 0)
        return [(item[0], item[1]/totalnum) for item in commands]
