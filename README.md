# py-redis-monitoring [![Build Status](https://travis-ci.org/saromanov/py-redis-monitoring.svg?branch=master)](https://travis-ci.org/saromanov/py-redis-monitoring) [![Coverage Status](https://coveralls.io/repos/saromanov/py-redis-monitoring/badge.svg?branch=master&service=github)](https://coveralls.io/github/saromanov/py-redis-monitoring?branch=master)


Monitoring of Redis commands

Supports: Python3.5

## Example
Server example:

```python
import redismonitor

def res(params):
    print("Receive: ", params)

result = redismonitor.Monitoring(backend='redis')
result.addServer('localhost', '6380')
result.addNotify('hset', res)
result.start()
```
In this example, we define backend for monitoring. At this stage, supports only redis. Note: Address for backend, should be different, than for monitoring. Then, add server for monitoring and add notification(optional) for command hset. Finnaly, start monitoring!


Client example:
```python
import redismonitor
result = redismonitor.ProcessingClient() # Client initialization
print(result.getCommandsStat()) # Get statistics for commands [('hset', 15), ('keys', 13), ('lpush', 5), ('dump', 2)]
print(result.getCommandsStat(host=b'127.0.0.1:50929')) # Get statistics by client address
print(result.getCommandsDistribution()) # Show command distribution [('hset', 0.42857142857142855), ('keys', 0.37142857142857144), ('lpush', 0.14285714285714285), ('dump', 0.05714285714285714)]
```
