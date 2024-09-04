import asyncio
import json
import websockets
from .core import Pupilio
from .web_socket_server import WebSocketServer


class SampleBroadcastServer(WebSocketServer):
    def __init__(self, host: str, port: int, pupil_io: Pupilio):
        """
        Initialize the Sample Broadcast Server.

        Args:
            host: Host address to run the server on.
            port: Port number to run the server on.
            pupil_io: An instance of DeepGaze class for data simulation.
        """
        super().__init__(host, port)
        self.host = host
        self.port = port
        self.connected_client_pool = set()
        self.pupil_io = pupil_io

    async def handle_client(self, websocket, path):
        """
        Handle client connections and actively send data to clients.

        Args:
            websocket: The WebSocket connection object.
            path: Path of the WebSocket connection (not used in this example).
            :param websocket:
            :param **kwargs:
        """
        self.connected_client_pool.add(websocket)
        try:
            while True:
                # 这里可以处理客户端发送的消息，或者不处理直接广播
                await asyncio.sleep(1)
        finally:
            # 移除断开的客户端连接
            self.connected_client_pool.remove(websocket)

    def broadcast(self, data):
        asyncio.run(self._broadcast(data))

    async def _broadcast(self, data):
        if self.connected_client_pool:
            for client in self.connected_client_pool:
                try:
                    json_data = json.dumps(data)
                    # print(json_data)
                    await client.send(json_data)
                except websockets.exceptions.ConnectionClosedError:
                    # If sending fails, remove the disconnected client
                    self.connected_client_pool.remove(client)
                    print("Client disconnected")
    # async def send_message(self, message):
    #     for client in self.broadcast_clients:
    #         try:
    #             await client.send(json.dumps(message))
    #         except websockets.exceptions.ConnectionClosedError:
    #             # If sending fails, remove the disconnected client
    #             self.connected_client_pool.remove(client)
    #             print("Client disconnected")


if __name__ == '__main__':
    # Usage example:
    # Create an instance of SampleBroadcastServer and start the server
    broadcast_server = SampleBroadcastServer("localhost", 8001, Pupilio())
