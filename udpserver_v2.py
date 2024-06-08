import socket
import time
import random
import threading
import sys


# 处理单个客户端的消息
def send_and_receive_packets(message, client_address, drop_rate, server_socket):
    try:
        recv_time = time.time()

        # 解析客户端数据
        seq_num = int.from_bytes(message[:2], byteorder='big')
        ver_num = int.from_bytes(message[2:3], byteorder='big')
        content = message[3:203]

        # 模拟丢包
        if random.random() < drop_rate:
            print(f"来自客户端 {client_address} 的丢包：Seq={seq_num}, Ver={ver_num}")
            return

        # 构造响应数据包
        response_time = str(recv_time).encode()
        response = seq_num.to_bytes(2, byteorder='big') + ver_num.to_bytes(1, byteorder='big') + len(
            response_time).to_bytes(2, byteorder='big') + response_time + b'z' * (198 - len(response_time))
        server_socket.sendto(response, client_address)

        print(
            f"收到客户端 {client_address} 的消息: Seq={seq_num}, Ver={ver_num}, Time={time.strftime('%H:%M:%S', time.localtime(recv_time))}")
    except Exception as e:
        print(f"处理客户端 {client_address} 的请求时出错: {e}")


# 监听键盘输入以便退出
def listen_for_exit(sock):
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
    listen_thread = threading.Thread(target=listen_for_exit, args=(server_socket,))
    listen_thread.start()

    while running:
        try:
            message, client_address = server_socket.recvfrom(2048)
            # 为每个客户端启动一个线程来处理
            client_thread = threading.Thread(target=send_and_receive_packets,
                                             args=(message, client_address, drop_rate, server_socket))
            client_thread.start()
        except socket.timeout:
            continue

    server_socket.close()
    print("服务器已关闭。")
