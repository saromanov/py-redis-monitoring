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