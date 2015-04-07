import redis
import datetime

class Monitoring:
	def __init__(self, host='localhost', port=6379):
		self.client = redis.ConnectionPool(host=host, port=port)
		self.processing = Processing()

	def start(self):
		""" Start monitoring """
		connect = self.client.get_connection('monitor', None)
		connect.send_command('monitor')
		print("monitoring has started...", datetime.datetime.now())
		while True:
			self.processing.receive_response(connect.read_response())

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

