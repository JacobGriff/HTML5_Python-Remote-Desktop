import asyncio
import traceback

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


async def send_init():
    # On init:
    # Client info
    # Ram & CPU Usage
    # Screenshot

    data = clientInfo._asdict()
    data.update({"resources": get_resources()})
    data.update({"screenshot": json.dumps(get_screenshot())})

    await send_msg("Init", data)


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

            if command == "Resources":
                await send_msg(command, get_resources())
            if command == "ToggleStream":
                stream = not stream
                print(f"Stream toggle set to: {stream}")

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
