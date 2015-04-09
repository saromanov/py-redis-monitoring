import redis
import datetime
import threading
import time

class Monitoring:
	def __init__(self, host='localhost', port=6379):
		self.servers = []
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


	def start(self):
		""" Start monitoring """
		for server in self.servers:
			self._createMonitor(server)
		while True:
			time.sleep(2)

class Processing:
	""" Processing and analytics receive commands """
	def __init__(self):
		self.host = {}

	def receive_response(self, response):
		if len(response) == 2:
			return 
		value = self._parse_response(response)
		iddata = value[0]
		self.host[value[1][1]] = {}
		self._parse_command(value[3:])

	def _parse_response(self, response):
		return response.split()

	def _parse_command(self, raw_command):
		print("this is command: ", raw_command)

