import asyncio
import json
import base64
import uuid

from websockets.asyncio.server import serve


# Classes

# Client class holds all the variables last sent by the client so we can update new web clients, and check for duplicate data
class Client:
    info = None
    screen = None
    screenSharing = False

    def __init__(self, clientid, socket):
        self.clientId = clientid
        self.socket = socket


class WebClient:
    def __init__(self, clientid, socket, connectedid):
        self.clientId = clientid
        self.socket = socket
        self.connectedId = connectedid


# This acts as the intermediary between the python client (machine) and the web client (browser)

clients = {}
webClients = {}


async def send_msg(websocket, command, data):
    # Identifies the sender, the command referenced, and the data passed

    msg = {"client": "Server", "command": command, "data": data}
    print("Sending: " + msg)

    await websocket.send(json.dumps(msg))


async def handler(websocket):

    #Types of data (all stored in json map so we can send and recieve via web sockets)
    #There's always a command and argument but only the web client sends the target for now since we're doing it based off that instead of establishing connections initially.

    #Web Client: (Doesnt need to say sender since itll update all web clients connected to this one
        #Command
        #Argumnets

    #Server: (Processes and forwards data, Doesnt need sender or target)
        #Command
        #Arguments

    #Client (Processes request and sends data back. Doesn't need sender or target since the server will determine web clients connected to send it to):
        #Command
        #Arguments

    try:
        async for message in websocket:
            receivedMap = json.loads(message)
            client = receivedMap["client"]
            command = receivedMap["command"]
            data = receivedMap["data"]

            print(f"Received map: {receivedMap}")

            targetClient = None

            if client == "WebClient":

                if command == "Init":
                    targetClient = receivedMap["target"]
                    clientUuid = uuid.uuid4()
                    webClient = WebClient(clientUuid, websocket, targetClient)
                    webClients.update({clientUuid : webClient})
                    continue

                print("Continue did not stop it!")

                # Send command to python client
                #targetClient = pythonClient


            print("Sending")

            if targetClient is not None:
                await send_msg(targetClient, command, data)

    except Exception as e:
        print(f"Connection closed: {e}")


async def main():
    async with serve(handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()  # run forever


asyncio.run(main())
