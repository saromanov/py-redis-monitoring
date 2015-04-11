import redis
import hashlib

class ProcessingClient:
	def __init__(self, backend='redis'):
		if backend == 'redis':
			self.client = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port='6399'))

	def getCommandStat(self, command):
		md5 = hashlib.md5()
		md5.update(b'127.0.0.1:47094')
		return self.client.hget(md5.hexdigest(), command)

	def getCommands(self):
		pass