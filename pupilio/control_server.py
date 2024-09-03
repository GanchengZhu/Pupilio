import json
import logging

import websockets

from .misc import ET_ReturnCode  # Importing the DeepGaze class from core module
from .web_socket_server import WebSocketServer
from .core import Pupilio


class ControlServer(WebSocketServer):
    def __init__(self, host, port, pupil_io: Pupilio):
        """
        Initialize the Control Server.

        Args:
            host: Host address to run the server on.
            port: Port number to run the server on.
            pupil_io: An instance of DeepGaze class for any specific function execution.
        """
        super().__init__(host, port)
        self.pupil_io = pupil_io  # Store the DeepGaze instance

    async def handle_client(self, websocket, path):
        """
        Handle client connections and execute commands received from clients.

        Args:
            websocket: The WebSocket connection object.
            path: Path of the WebSocket connection (not used in this example).
        """
        logging.info("Client connected to control websocket")
        try:
            async for message in websocket:
                # Receive command from the client
                command = message.strip()
                command_dict = json.loads(command)
                # Execute a specific function, here it just prints and sends a success message back
                logging.info(f"Received command: {command}")
                logging.info(command_dict)
                result = {}
                # Check if the command is a valid method name in DeepGaze
                if "function" in command_dict.keys():
                    function = command_dict["function"]
                    if hasattr(self.pupil_io, function) and callable(getattr(self.pupil_io, function)):
                        # Use getattr to get the method by name and execute it
                        if function == "face_position":
                            status, face_position = self.pupil_io.face_position()
                            result = {
                                "function": function,
                                "status": status,
                                "face_position": face_position.tolist()
                            }
                        elif function == "calibration" and function == "create_session":
                            call = getattr(self.pupil_io, function)
                            call_result = call(*command_dict["args"])
                            result = {
                                "function": function,
                                "status": call_result,
                            }
                        elif function == "estimation":
                            status, gaze_sample, timestamp, trigger = self.pupil_io.estimation()
                            result = {
                                "function": function,
                                "status": status,
                                "gaze_sample": gaze_sample.tolist(),
                                "timestamp": timestamp,
                                "trigger": trigger
                            }
                        elif function == "estimation_lr":
                            (status, left_gaze_sample, right_gaze_sample, timestamp,
                             trigger) = self.pupil_io.estimation_lr()
                            result = {
                                "function": function,
                                "status": status,
                                "left_gaze_sample": left_gaze_sample.tolist(),
                                "right_gaze_sample": right_gaze_sample.tolist(),
                                "timestamp": timestamp,
                                "trigger": trigger
                            }
                        else:
                            call = getattr(self.pupil_io, function)
                            call_result = call()
                            result = {
                                "function": function,
                                "status": call_result,
                            }
                elif "send_trigger" in command_dict.keys():
                    trigger = command_dict["send_trigger"]
                    self.pupil_io.set_trigger(trigger)

                    result = {
                        "send_trigger": trigger,
                        "status": int(ET_ReturnCode.ET_SUCCESS),
                        "message": f"{trigger} received"
                    }
                    # mark the current example
                else:
                    result = {
                        "send_trigger": -1,
                        "status": -1,
                        "message": "Invalid Function"
                    }
                # Send the execution result back to the client
                await websocket.send(json.dumps(result))
        except websockets.exceptions.ConnectionClosedError:
            logging.info("Client disconnected")


if __name__ == '__main__':
    pass
