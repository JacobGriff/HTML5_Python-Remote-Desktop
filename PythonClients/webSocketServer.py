import io
import base64
import json
import asyncio
import traceback
import uuid
import pyautogui

from websockets.asyncio.server import serve


# Classes

# Client class holds all the variables last sent by the client so we can update new web clients, and check for duplicate data
class Client:

    #Data
    info = None
    screenShot = None

    #Toggles
    screenSharing = False

    def __init__(self, clientid, socket):
        self.clientId = str(clientid)
        self.socket = socket


class WebClient:
    connectedId = None

    def __init__(self, clientid, socket):
        self.clientId = str(clientid)
        self.socket = socket

    def socketMatches(self, other_socket):
        return self.socket == other_socket


def getScreenshot():
    # Take screenshot
    screenshot = pyautogui.screenshot()

    # Convert to bytes
    with io.BytesIO() as buffer:
        screenshot.save(buffer, format="JPEG", quality=70)
        img_bytes = buffer.getvalue()

    # Convert to Base64 string
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return json.dumps(img_b64)

# This acts as the intermediary between the python client (machine) and the web client (browser)

pythonClients = list()

#Add fake client for testing
fakeClient = Client("1234", None)
fakeClient.screenShot = getScreenshot()
fakeClient.info = "CPU: 100% | RAM: 50%"
pythonClients.append(fakeClient)

webClients = list()



def getWebClient(socket) -> WebClient:
    for webClient in webClients:
        if webClient.socketMatches(socket):
            return webClient

    return None


def getHubInfo() -> list:
    allClients = list()
    for client in pythonClients:
        data = {"Id": client.clientId, "Info": client.info, "Screenshot": client.screenShot}
        allClients.append(data)

    return allClients


async def send_msg(websocket, command, data):
    # Identifies the sender, the command referenced, and the data passed

    msg = {"client": "Server", "command": command, "data": data}
    print("Sending: " + str(msg))

    await websocket.send(json.dumps(msg))


async def handleWebClientRequest(websocket, client, command, data):
    if command == "Init":
        clientUuid = uuid.uuid4()
        webClient = WebClient(clientUuid, websocket)
        webClients.append(webClient)
        # Maybe add something else
        await send_msg(websocket, "Init", True)
        return

    # Get the web client based on websocket
    webClient = getWebClient(websocket)

    if webClient is None:
        print("This shouldn't be none...")
        return

    if command == "GetClients":
        await send_msg(websocket, "GetClients", getHubInfo())
        return

    if command == "ConnectTo":
        # Make sure it exists
        foundClient = False
        for client in pythonClients:
            if client.clientId == data:
                foundClient = True

        if foundClient:
            webClient.connectedId = data
            print(f"Connected web client {webClient.clientId} to {data}")
            await send_msg(websocket, "ConnectTo", data)
        else:
            print(f"Failed to connect web client {webClient.clientId} to {data} as that desktop client does not exist.")
            await send_msg(websocket, "ConnectTo", None)

        return

        # Otherwise send command to python client
    # targetClient = pythonClient


async def handler(websocket):
    # Types of data (all stored in json map so we can send and recieve via web sockets)
    # There's always a command and argument but only the web client sends the target for now since we're doing it based off that instead of establishing connections initially.

    # Web Client: (Doesnt need to say sender since itll update all web clients connected to this one
    # Command
    # Argumnets

    # Server: (Processes and forwards data, Doesnt need sender or target)
    # Command
    # Arguments

    # Client (Processes request and sends data back. Doesn't need sender or target since the server will determine web clients connected to send it to):
    # Command
    # Arguments

    try:
        async for message in websocket:
            receivedMap = json.loads(message)
            client = receivedMap["client"]
            command = receivedMap["command"]
            data = receivedMap["data"]

            print(f"Received map: {receivedMap}")

            if client == "WebClient":
                await handleWebClientRequest(websocket, client, command, data)

    except Exception as e:
        print(f"Connection closed: {repr(e)}")  # exact type + message
        traceback.print_exc()  # full stack trace


async def main():
    async with serve(handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()  # run forever


asyncio.run(main())
