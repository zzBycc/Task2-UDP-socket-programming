import socket
import time
import random
import threading
import sys


# 模拟TCP连接的建立过程
def build_tcp_like_connection(sock):
    try:
        # 接收客户端的SYN包
        syn_message, address = sock.recvfrom(2048)
        if syn_message == b'\x00\x01' + 'SYN'.encode():
            # 发送SYN-ACK包
            server_socket.sendto(b'\x00\x02' + 'SYN-ACK'.encode(), address)
            # 接收客户端的ACK包
            ack_message, _ = server_socket.recvfrom(2048)
            if ack_message == b'\x00\x04' + 'ACK'.encode():
                print(f"TCP式连接已建立:{address}")
            return address
    except socket.timeout:
        print('模拟TCP连接建立失败！')
        return False


# 处理来自客户端的数据
def send_and_receive_packets(server_socket, drop_rate):
    global running
    while running:
        try:
            server_socket.settimeout(1.0)
            message, client_address = server_socket.recvfrom(2048)
            recv_time = time.time()

            # 模拟TCP连接释放过程
            if message == b'\x00\x03' + 'FIN'.encode():
                server_socket.sendto(b'\x00\x04' + 'ACK'.encode(), client_address)
                server_socket.sendto(b'\x00\x03' + 'FIN'.encode(), client_address)
                print("服务器正在关闭...")
                ack_message, _ = server_socket.recvfrom(2048)
                if ack_message == b'\x00\x04' + 'ACK'.encode():
                    break

            # 解析客户端数据
            seq_num = int.from_bytes(message[:2], byteorder='big')
            ver_num = int.from_bytes(message[2:3], byteorder='big')
            content = message[3:203]

            # 模拟丢包
            if random.random() < drop_rate:
                print(f"来自客户端{client_address}的丢包：Seq={seq_num}, Ver={ver_num}")
                continue

            # 构造响应数据包
            # response_time = time.strftime('%H:%M:%S', time.localtime(recv_time)).encode()
            response_time = str(recv_time).encode()
            response = seq_num.to_bytes(2, byteorder='big') + ver_num.to_bytes(1,
                                                                               byteorder='big') + len(
                response_time).to_bytes(2, byteorder='big') + response_time + b'z' * (
                               198 - len(response_time))
            server_socket.sendto(response, client_address)

            print(
                f"收到客户单{client_address}的消息: Seq={seq_num}, Ver={ver_num}, Time={time.strftime('%H:%M:%S', time.localtime(recv_time))}")
        except socket.timeout:
            # 超时继续循环，检查running状态
            continue


def listen_for_exit(sock):
    # 监听键盘输入以便退出
    global running
    while running:
        cmd = input()
        if cmd.strip().lower() == 'exit':
            print("关闭服务器...")
            running = False
            sock.close()
            break
        else:
            print("无效命令！")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('参数不足！<serverPort> <drop_rate>')
        sys.exit(1)

    server_port = int(sys.argv[1])  # 服务器端口
    drop_rate = float(sys.argv[2])  # 丢包率
    running = True  # 控制exit线程和服务器接收数据

    # 创建并绑定UDP服务器socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print("----服务器启动----")

    # 启动exit线程，控制输入exit终止服务器
    print("输入 exit 可以关闭服务器")
    listen_thread = threading.Thread(target=listen_for_exit, args=(server_socket,))
    listen_thread.start()

    if build_tcp_like_connection(server_socket):
        send_and_receive_packets(server_socket, drop_rate)

    server_socket.close()
    print("服务器已关闭。")

