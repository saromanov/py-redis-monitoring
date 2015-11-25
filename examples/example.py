import redismonitor


def res(params):
    print("Receive: ", params)


def basic_run():
    result = redismonitor.Monitoring(show_every=10, backend='redis')
    result.addServer('localhost', '6380')
    result.addNotify('hset', res)
    result.start()

if __name__ == '__main__':
    basic_run()
