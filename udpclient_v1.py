import socket
import time
import numpy as np
import sys


# 模拟TCP连接建立过程
def build_tcp_like_connection(sock, ip, port):
    try:
        # 发送SYN包
        sock.sendto(b'\x00\x01' + 'SYN'.encode(), (ip, port))
        syn_ack_message, server_address = sock.recvfrom(2048)
        # 接收SYN-ACK包
        if syn_ack_message == b'\x00\x02' + 'SYN-ACK'.encode():
            # 发送ACK包
            sock.sendto(b'\x00\x04' + 'ACK'.encode(), (ip, port))
            print('模拟TCP连接建立成功。')
            return True
    except socket.timeout:
        print('模拟TCP连接建立失败！')
        return False


# 发送数据包并接收响应，计算RTT
def send_and_receive_packets(sock, ip, port, nums, ver):
    rtts = []  # 往返时间
    packets_cnt = 0  # 接收的数据包数量
    # 响应时间
    last_time = None
    first_time = None
    for i in range(nums):  # 发送 nums 个请求数据包
        # 构造报文格式
        seq_num = i + 1
        request_message = seq_num.to_bytes(2, byteorder='big') + ver.to_bytes(1, byteorder='big') + b'zwb#' * 50
        send_time = time.time()
        times_cnt = 0
        while times_cnt < 3:  # 最多重传两次
            sock.sendto(request_message, (ip, port))  # 发送数据包
            try:
                response_message, server_address = sock.recvfrom(2048)  # 接收响应
                # 解析响应
                rcv_seq_num = int.from_bytes(response_message[:2], byteorder='big')
                rcv_ver = int.from_bytes(response_message[2:3], byteorder='big')
                rcv_time_len = int.from_bytes(response_message[3:5], byteorder='big')
                # response_time = response_message[5:rcv_time_len + 5].decode()
                # 将接收到的时间字符串转换为时间戳
                # response_timestamp = time.mktime(time.strptime(response_time, '%H:%M:%S'))
                response_time = float(response_message[5:rcv_time_len + 5].decode())

                # 记录第一次和最后一次响应的时间
                if first_time is None:
                    first_time = response_time
                last_time = response_time

                # 计算RTT
                rcv_time = time.time()
                rtt = (rcv_time - send_time) * 1000  # ms -> s
                rtts.append(rtt)
                packets_cnt += 1

                # 打印RTT
                print(f"接收数据: Seq={rcv_seq_num}, Ver={rcv_ver}, Server={server_address}, RTT={rtt:.2f}ms")
                break
            except socket.timeout:
                times_cnt += 1
                print(f'请求超时：序列号={seq_num}，尝试次数={times_cnt}')
    return rtts, packets_cnt, first_time, last_time


# 模拟TCP连接释放过程
def terminate_tcp_like_connection(sock, server_ip, server_port):
    try:
        sock.sendto(b'\x00\x03' + 'FIN'.encode(), (server_ip, server_port))
        ack_message, server_address = sock.recvfrom(2048)
        if ack_message == b'\x00\x04' + 'ACK'.encode():
            fin_message, server_address = sock.recvfrom(2048)
            if fin_message == b'\x00\x03' + 'FIN'.encode():
                sock.sendto(b'\x00\x04' + 'ACK'.encode(), (server_ip, server_port))
                print('模拟TCP连接关闭成功')
    except socket.timeout:
        print('模拟TCP关闭连接超时！')


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('参数不足！<serverIP> <serverPort> <packet_nums> <packet_ver> <timeout>')
        sys.exit(1)

    server_ip = sys.argv[1]  # 服务器IP地址
    server_port = int(sys.argv[2])  # 服务器端口号
    packet_nums = int(sys.argv[3])  # 要发送的数据报数量
    packet_ver = int(sys.argv[4])  # 数据包的版本
    timeout = float(sys.argv[5])  # 超时时间参数

    # 创建并配置UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    if build_tcp_like_connection(client_socket, server_ip, server_port):
        Rtts, received_packets, first_response_time, last_response_time = \
            send_and_receive_packets(client_socket, server_ip, server_port, packet_nums, packet_ver)
        if Rtts:
            print("\n-----汇总信息-----")
            print(f'接收到的数据包数：{received_packets}，数据包丢失率：{(1 - received_packets / packet_nums) * 100:.2f}%')
            print(f'最大RTT：{max(Rtts):.2f} ms')
            print(f'最小RTT：{min(Rtts):.2f} ms')
            print(f'平均RTT：{np.mean(Rtts):.2f} ms')
            print(f'RTT标准差：{np.std(Rtts):.2f} ms')
            print(f"server的整体响应时间{last_response_time - first_response_time:.2f} s")

        else:
            print('未接收到任何响应数据包。')
        terminate_tcp_like_connection(client_socket, server_ip, server_port)
    else:
        client_socket.close()
        print("客户端套接字已关闭。")
