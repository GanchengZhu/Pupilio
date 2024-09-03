import asyncio

import websockets


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.start_server = websockets.serve(self.handle_client, self.host, self.port)

    async def handle_client(self, websocket, path):
        pass

    async def start(self):
        """
        Start the WebSocket server.
        """
        await self.start_server

    def run_forever(self):
        asyncio.get_event_loop().run_forever()
