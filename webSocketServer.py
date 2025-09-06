import io
import base64
import json
import asyncio
import traceback
import uuid
import pyautogui
import websockets.asyncio.server
import PIL.Image

from websockets.asyncio.server import serve


# Classes

# Client class holds all the variables last sent by the client so we can update new web clients, and check for duplicate data
class Client:
    # System info

    # Toggles always off at the start
    screenSharing = False

    def __init__(self, socket, clientid, system, version, architecture, resources, screenshot, rootdrives):
        self.socket = socket
        self.clientId = str(clientid)
        self.system = str(system)
        self.version = str(version)
        self.architecture = str(architecture)
        self.resources = resources
        self.screenShot = screenshot
        self.rootDrives = rootdrives

    def get_info(self):
        return self.system + " " + self.version + " " + self.architecture

    def get_all_data(self):
        return {"system": self.system, "version": self.version, "architecture": self.architecture,
                "resources": self.resources, "screenshot": self.screenShot, "rootDrives": self.rootDrives}

    def id_matches(self, other_id):
        return self.clientId == other_id

    def socket_matches(self, other_socket):
        return self.socket == other_socket


class WebClient:

    def __init__(self, socket, clientid, pythonclientid):
        self.socket = socket
        self.clientId = str(clientid)
        self.pythonClientId = pythonclientid

    def socketMatches(self, other_socket):
        return self.socket == other_socket

    def python_client_matches(self, other_clientid):
        return self.pythonClientId == other_clientid


def get_screenshot():
    # Take screenshot
    screenshot = pyautogui.screenshot()

    # Convert to bytes
    with io.BytesIO() as buffer:
        screenshot.save(buffer, format="JPEG", quality=70)
        img_bytes = buffer.getvalue()

    # Convert to Base64 string so it can be json dumped in send_msg
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    return json.dumps(img_b64)


# This acts as the intermediary between the python client (machine) and the web client (browser)

pythonClients = list()

# Add fake client for testing
fakeClient = Client(None, "Example PC", "Windows", "10", "AMDx64", {"CPU": "100", "RAM": "50%"}, get_screenshot(),
                    "Test")
pythonClients.append(fakeClient)

webClients = list()


def getWebClient(socket) -> WebClient:
    for webClient in webClients:
        if webClient.socketMatches(socket):
            return webClient

    return None


def getPythonClientIndex(id):
    for index, client in enumerate(pythonClients):
        if client.id_matches(id):
            return index

    return None


def getPythonClientFromId(id) -> Client:
    for client in pythonClients:
        if client.id_matches(id):
            return client

    return None


def getPythonClientSocket(id) -> websockets.asyncio.server.ServerConnection:
    matchedSocket = None

    for client in pythonClients:
        if client.id_matches(id):
            matchedSocket = client.socket

    return matchedSocket


def getPythonClientFromSocket(websocket) -> Client:
    for pythonClient in pythonClients:
        if pythonClient.socket_matches(websocket):
            return pythonClient

    return None


def getConnectedWebClientSockets(websocket):
    global webClients
    activeWebClients = list()
    connectedWebClients = list()

    # Get python client from web socket since we dont want to store target sockets in every web client. We could, but dont need big data stored like that
    pythonClient = getPythonClientFromSocket(websocket)

    if pythonClient is None:
        return connectedWebClients

    pythonClientId = pythonClient.clientId

    # Get all web clients whos target is this
    # Also confirm web client is still active! Otherwise clean up

    for webClient in webClients:
        # Make sure socket is available!
        socket = webClient.socket
        socketClosed = socket.state == 3

        # Don't add to new array
        if socketClosed:
            print("Found closed web client")
            continue

        # Add live clients to array
        activeWebClients.append(webClient)

        # If it matches return
        if webClient.python_client_matches(pythonClientId):
            connectedWebClients.append(webClient.socket)

    webClients = activeWebClients

    return connectedWebClients


def getHubInfo() -> list:
    allClients = list()
    for client in pythonClients:
        data = {"Id": client.clientId, "Info": client.get_info(), "Resources": client.resources,
                "Screenshot": client.screenShot}
        allClients.append(data)

    return allClients


async def send_msg(websocket, command, data):
    # Returns true if it was a success, and false if fail. This way we can clean up closed sockets if it made it through all other checks.

    # Identifies the sender, the command referenced, and the data passed

    msg = {"client": "Server", "command": command, "data": data}
    print("Sending: " + str(msg)[:200])

    # Make sure socket is active
    socketClosed = websocket.state == 3
    if socketClosed:
        print("Error, this socket is in a closed state. Aborting. Please perform checks before passing sockets here.")
        return False

    await websocket.send(json.dumps(msg))
    return True


async def send_msg_to_all_web_clients(pythonClientSocket, command, data):
    # This gets only web sockets that are connected to this python client
    # Additionally, it checks for any closed web sockets and cleans them up
    webClientSockets = getConnectedWebClientSockets(pythonClientSocket)
    for webClientSocket in webClientSockets:
        await send_msg(webClientSocket, command, data)


async def handleWebClientRequest(websocket, command, data):
    if command == "Init":
        print("Establishing Web Client Connection")
        clientUuid = uuid.uuid4()
        pythonClient = data
        webClient = WebClient(websocket, clientUuid, pythonClient)
        webClients.append(webClient)

        print(f"Total web clients {len(webClients)}")

        # Maybe add something else
        await send_msg(websocket, "Init", True)
        return

    # Get the web client based on websocket
    webClient = getWebClient(websocket)

    # Testing client or bad data send
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

    # Pull all saved data for its client and send back to web client. Meant for first connection. Doesn't send to python client or other web clients.
    if command == "PullSaved":
        print("Sending back all saved data")
        pythonClient = getPythonClientFromId(webClient.pythonClientId)
        if pythonClient is not None:
            data = pythonClient.get_all_data()
            await send_msg_to_all_web_clients(pythonClient.socket, "PullSaved", data)
            return

    # Otherwise send command to python client

    print("Sending request to python client")

    pythonClientSocket = getPythonClientSocket(webClient.pythonClientId)

    socketClosed = websocket.state == 3

    if pythonClientSocket is not None and not socketClosed:
        await send_msg(pythonClientSocket, command, data)
    else:
        print(f"Failed, not connected to python client. Python client id: {webClient.pythonClientId} "
              f"| Error: {'Socket is null' if pythonClientSocket is None else 'Socket is closed'}")


async def handlePythonClientRequest(clientWebSocket, command, data):

    # Try to get existing client if it exists using its websocket
    client = getPythonClientFromSocket(clientWebSocket)

    if command == "Init":
        print("Establishing client connection")
        print(f"Data: {str(data)[:200]}")

        # Check for existing client with this id
        clientId = data["node"]
        existingClient = getPythonClientFromId(clientId)

        # Existing client reconnected. Update vars
        if existingClient is not None:
            print("Client already exists. Updating data")
            existingClient.resources = data["resources"]
            existingClient.screenShot = data["screenshot"]
            existingClient.rootDrives = data["rootDrives"]
            existingClient.socket = clientWebSocket
            client = existingClient
        else:
            # Create new client
            client = Client(clientWebSocket, clientId, data["system"], data["release"], data["machine"], data["resources"],
                            data["screenshot"], data["rootDrives"])
            pythonClients.append(client)

        print(f"Total clients: {len(pythonClients)}")

        # On success send init back to the python client, and send all data to web clients trying to view it
        await send_msg(clientWebSocket, "Init", True)

        data = client.get_all_data()
        await send_msg_to_all_web_clients(clientWebSocket, "PullSaved", data)

        return

    if command == "FileTest":
        b64 = base64.b64decode(data)
        file = io.BytesIO(b64)
        img = PIL.Image.open(file)
        img.show()

    # Now for whatever command entered, update vars to create save state!

    print("Updating values broskie")

    if command == "Screenshot":
        client.screenShot = data
    elif command == "Resources":
        client.resources = data
        print("Updated resources data")

    # Other commands to send to all web clients

    await send_msg_to_all_web_clients(clientWebSocket, command, data)


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

            dataStr = str(data)

            print(f"Client: [ {client} | Command: {command} | Data {dataStr[:500]} ] ")

            if client == "WebClient":
                await handleWebClientRequest(websocket, command, data)
            elif client == "PyClient":
                await handlePythonClientRequest(websocket, command, data)

    except Exception as e:
        print(f"Connection closed: {repr(e)}")  # exact type + message
        traceback.print_exc()  # full stack trace


async def main():
    print("Main Started")

    async with serve(handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()  # run forever


asyncio.run(main())
