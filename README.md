# Task2-UDP-socket-programming
程序运行环境：python3.12、numpy3.12

简单说明：v1 为模仿TCP连接和释放的版本，由于在此过程中会阻塞，所以不支持多客户端连接；
	 v2为多个客户端同时连接的版本，UDP本身就能处理多端连接，前提是没有模仿TCP连接和释放的阻塞，该版本还使用了线程，用于避免阻塞。

测试样例：

1. 服务器：<serverPort> <drop_rate>
    v1版本：
    python udpserver_v1.py 50007 0.5

    v2版本：
    python udpserver_v2.py 50007 0.5

2. 客户端：<serverIP> <serverPort> <packet_nums> <packet_ver> <timeout>
    v1 版本抓包：
    python udpclient_v1.py 127.0.0.1 50007 10 1 0.1

    v2版本测试多个客户端同时连接：
    python udpclient_v2.py 127.0.0.1 50007 100 1 0.1
    python udpclient_v2.py 127.0.0.1 50007 100 2 0.1

   

