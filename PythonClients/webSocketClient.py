import asyncio
import websockets
import psutil
import json
import base64
import io
import pyautogui

client = "PyClient"
socket = None

# Data

stream = False


async def send_msg(websocket, command, data):
    msg = {"client": client, "command": command, "data": data}
    print(f"Sending: {msg}")
    await websocket.send(json.dumps(msg))


async def streamScreen():
    while True:
        if stream:
            # Take screenshot
            screenshot = pyautogui.screenshot()

            # Convert to bytes
            with io.BytesIO() as buffer:
                screenshot.save(buffer, format="JPEG", quality=70)
                img_bytes = buffer.getvalue()

            # Convert to Base64 string
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # Wrap in JSON for metadata
            msg = {
                "client": client,
                "command": "Image",
                "data": img_b64
            }

            await socket.send(json.dumps(msg))

        await asyncio.sleep(1 / 100)


async def send_info(websocket):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    info = {"Cpu": cpu, "Memory": memory}

    await send_msg(websocket, "Info", info)


async def awaitRequests(websocket):
    global stream
    while True:
        message = await websocket.recv()
        receivedMap = json.loads(message)
        client = receivedMap["client"]
        data = receivedMap["data"]
        command = receivedMap["command"]

        print(f"Received: {receivedMap}")

        if command == "Info":
            await send_info(websocket)
        if command == "ToggleStream":
            stream = not stream
            print(f"Stream toggle set to: {stream}")


async def main():
    uri = "ws://localhost:8765"
    global socket
    async with websockets.connect(uri) as websocket:  # <-- async API
        await send_msg(websocket, "Init", "Client: Python client")

        socket = websocket

        await asyncio.gather(
            streamScreen(),
            awaitRequests(websocket)
        )


asyncio.run(main())
