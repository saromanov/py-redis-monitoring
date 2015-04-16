import redis
import hashlib

class ProcessingClient:
	def __init__(self, backend='redis'):
		if backend == 'redis':
			self.client = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port='6399'))

	def _processHost(self, host):
		md5 = hashlib.md5()
		md5.update(host)
		return md5.hexdigest()

	def getCommandStat(self, command, host='allhosts'):
		if host != 'allhosts':
			host = self._processHost(host)
		return self.client.hget(host, command)

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
		result = list(map(lambda x: (x, self.getCommandStat(x, host=host)), self.client.hkeys(host)))
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