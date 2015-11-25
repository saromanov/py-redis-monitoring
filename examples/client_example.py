import redismonitor


def main():
    result = redismonitor.ProcessingClient()
    print(result.getCommandsStat())
    print(result.getCommandsDistribution())
    result.removeData()

if __name__ == '__main__':
    main()
