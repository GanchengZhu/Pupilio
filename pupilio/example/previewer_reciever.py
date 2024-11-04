import socket
import numpy as np
import cv2

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 定义服务器地址和端口
sock.bind(('127.0.0.1', 8848))

# 创建一个窗口
cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

while True:
    # 发送测试数据到服务器
    # message = b'Test message'
    # sock.sendto(message, server_address)

    # 接收数据
    data, addr = sock.recvfrom(1024 * 1024)

    # 如果没有数据可接收，则等待
    if not data:
        break

    # 将字节转换为帧
    np_data = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(np_data, cv2.IMREAD_GRAYSCALE)

    if frame is None:
        print("Received invalid frame.")
        continue  # 跳过本次循环

    # 显示帧
    cv2.imshow('Video', frame)

    # 按'q'退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.close()
cv2.destroyAllWindows()
