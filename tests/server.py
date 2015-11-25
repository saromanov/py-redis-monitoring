import redismonitor

result = redismonitor.Monitoring(backend='redis')
result.addServer('localhost', '6380')
result.start()

