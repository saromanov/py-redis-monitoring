import client

def main():
	result = client.ProcessingClient()
	print(result.getCommandStat('hset'))

if __name__ == '__main__':
	main()