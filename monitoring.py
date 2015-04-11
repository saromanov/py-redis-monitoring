import redis
import datetime
import threading
import time
from collections import Counter
import hashlib

class Monitoring:
	"""
		clearall - clear all store before start monitoring 
	"""
	def __init__(self, host='localhost', port=6379, show_every=10, clearall=False):
		self.servers = []
		self.show_every = show_every
		#self.client = redis.ConnectionPool(host=host, port=port)
		self.processing = Processing()

	def _createClient(self,host, port):
		return redis.ConnectionPool(host=host, port=port)

	def addServer(self, host, port):
		self.servers.append({'host':host, 'port':port})

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

	def getter1(self, value):
		print(value)


	def start(self, addr='localhost'):
		""" Start monitoring """
		for server in self.servers:
			self._createMonitor(server)
		while True:
			time.sleep(2)

class Processing:
	""" Processing and analytics receive commands """
	def __init__(self):
		self.host = {}
		self.commands_stat = Counter()
		self.redis_store = RedisWrite('localhost', '6399')

	def receive_response(self, response):
		if len(response) == 2:
			return 
		addr, command, params = self._parse_response(response)
		self.commands_stat[command] += 1
		md5 = hashlib.md5()
		md5.update(addr)
		self.redis_store.putEvent(md5.hexdigest(), command, params)
		#self.host[value[1][1]] = {}

	def _parse_response(self, response):
		raw = response.split()
		addr = raw[2][:-1]
		command = raw[3][1:-1]
		params = raw[4:]
		return addr, command, params

	def show_commands_stat(self):
		return self.commands_stat


class RedisWrite:
	def __init__(self, host, port):
		self.client = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=host, port=port))

	def putEvent(self, addr, command, params):
		self.client.hincrby(addr, command)

class Event:
	def __init__(self, addr, command, params):
		self.addr = addr
		self.command = command
		self.params = params

