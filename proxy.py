from proxyscrape import create_collector

collector = create_collector("my-collector", "https")

# Retrieve any http proxy
proxygrab = collector.get_proxy({'code': ('us')})
proxy = ("{}:{}".format(proxygrab.host, proxygrab.port))
print ('\033[31m' + "Proxy:", proxy + '\033[0m')