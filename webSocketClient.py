import asyncio
import traceback
import os
import websockets
import psutil
import json
import base64
import io
import pyautogui
import platform

client = "PyClient"
socket = None
fps = 100

# Delays (asyncio.sleep) in seconds
frameDelay = 1 / fps
reconnectDelay = 1

# Data

stream = False

clientInfo = platform.uname()


async def send_msg(command, data):
    global socket
    msg = {"client": client, "command": command, "data": data}
    print(f"Sending: {str(msg)[:500]}")
    await socket.send(json.dumps(msg))


# Returns storage in bytes to whatever the most appropriate value is (such as GB), rounded and into a string
def get_storage_str(size) -> str:
    kb = 1000
    mb = kb * 1000
    gb = mb * 1000
    tb = gb * 1000

    divider = 1

    # Is there a better word to describe these than abbreviation?
    abbreviation = "B"

    if kb <= size < mb:
        divider = kb
        abbreviation = "KB"
    elif mb <= size < gb:
        divider = mb
        abbreviation = "MB"
    elif gb <= size < tb:
        divider = gb
        abbreviation = "GB"
    elif size >= tb:
        divider = tb
        abbreviation = "TB"

    reducedValue = round(size / divider)
    return str(reducedValue) + abbreviation


def get_size(path) -> str:
    if os.path.isdir(path):
        # return getFolderSize(path)
        return None

    size = os.path.getsize(path)
    return get_storage_str(size)


async def get_files(directory):

    #Clean up path
    directory = os.path.normpath(directory)

    print(f"Getting path: {directory}")

    # Javascript Web Client code: var files = {"Dir": "C:\\", "Files": rootDrives["C:\\"]["Files"]}
    # Python example files = {"Dir: ": "C:\\", "Files": {"image.png": "100MB", "Desktop": None}}
    dictionary = {"Dir": directory}

    fileMap = {}

    try:
        fileList = os.listdir(directory)

        for file in fileList:
            path = str(os.path.join(directory, file))
            size = get_size(path)
            fileMap.update({file: size})

        dictionary.update({"Files": fileMap})

        await send_msg("GetFiles", dictionary)
    except PermissionError as error:
        await send_msg("PermissionError", str(error))


async def get_parent_directory(dir):
    parent = os.path.dirname(dir)

    #Hit root so return drives
    if parent == dir:
        return await send_msg("GetDrives", get_drives())

    await get_files(parent)


def get_drives():
    # First get all drives
    partitions = psutil.disk_partitions()
    drives = list()
    for partition in partitions:
        drives.append(partition.device)

    # Get drives and storages into string list
    driveInfo = {}
    for drive in drives:
        usage = psutil.disk_usage(drive)
        driveInfo[drive] = {
            "Free": get_storage_str(usage.free),
            "Total": get_storage_str(usage.total),
        }

    return driveInfo


async def send_init():
    # On init:
    # Client info
    # Ram & CPU Usage
    # Screenshot
    # Root Drives

    data = clientInfo._asdict()
    data.update({"resources": get_resources()})
    data.update({"screenshot": json.dumps(get_screenshot())})
    data.update({"rootDrives": get_drives()})

    await send_msg("Init", data)
    # await send_file("C:/Users/Void/OneDrive/Desktop/Eye chart.png")


def get_screenshot():
    # Take screenshot
    screenshot = pyautogui.screenshot()

    # Convert to bytes
    with io.BytesIO() as buffer:
        screenshot.save(buffer, format="JPEG", quality=70)
        img_bytes = buffer.getvalue()

    # Convert to Base64 string so it can be json dumped in send_msg
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_b64


async def get_file(dir):
    file = open(dir, "rb")
    b64 = base64.b64encode(file.read()).decode("utf-8")
    return b64


def get_resources():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    return {"Cpu": cpu, "Memory": memory}


async def frameHandler():
    # Handles sending data every frame update based on toggles
    global socket

    while True:

        # Attempt to restablish connection once per second
        if not socket:
            return

        if stream:
            await send_msg("Screenshot", get_screenshot())

        await asyncio.sleep(frameDelay)


async def awaitRequests(websocket):
    global stream
    global socket

    while True:

        if not socket:
            await asyncio.sleep(reconnectDelay)
            return

        try:

            message = await websocket.recv()
            receivedMap = json.loads(message)
            client = receivedMap["client"]
            data = receivedMap["data"]
            command = receivedMap["command"]

            print(f"Received: {receivedMap}")

            if command == "Init":
                # Failed to connect?
                if not data:
                    socket = None

            elif command == "Resources":
                await send_msg(command, get_resources())

            elif command == "ToggleStream":
                stream = not stream
                print(f"Stream toggle set to: {stream}")

            elif command == "GetFiles":
                await get_files(data)

            elif command == "BackDirectory":
                await get_parent_directory(data)

        except websockets.exceptions.ConnectionClosedError as e:
            await onConnectionClosed(e)
            return

        except websockets.exceptions.ConnectionClosedOK as e:
            await onConnectionClosed(e)
            return

        except websockets.exceptions.ConnectionClosed as e:
            await onConnectionClosed(e)
            return

        # Other exceptions
        except Exception as e:
            print(f"Error: {repr(e)}")
            traceback.print_exc()  # full stack trace


async def onConnectionClosed(error):
    global socket

    print(f"Connection to server closed: {repr(error)}")  # exact type + message

    socket = None


async def establishConnection():
    uri = "ws://localhost:8765"
    global socket

    try:
        print("Connecting to server")
        async with websockets.connect(uri) as websocket:  # <-- async API
            print(f"Connected to server: {uri}")
            socket = websocket

            await send_init()
            await asyncio.gather(frameHandler(), awaitRequests(websocket))

    except Exception as e:
        print(f"Unable to connect: {repr(e)}")  # exact type + message
        await asyncio.sleep(reconnectDelay)


async def main():
    global socket

    print("Client started")

    # Connection loop
    while True:
        # This will only ever finish once the connection fails
        await establishConnection()
        await asyncio.sleep(reconnectDelay)
        print("Attempting to reconnect")


asyncio.run(main())
