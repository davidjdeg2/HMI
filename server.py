import asyncio
import websockets
import struct

# Mapping of hex identifiers to parameter names
identifier_mapping = {
    0x01: 'battery_soc',
    0x02: 'temperature',
    # You can add more mappings here
}

async def receive_messages(websocket):
    """Listen for incoming messages from the server and process them."""
    try:
        async for message in websocket:
            if len(message) == 5:
                identifier, value = struct.unpack('!Bf', message)
                parameter_name = identifier_mapping.get(identifier, f"Unknown(0x{identifier:02X})")
                print(f"Received: {parameter_name} = {value:.2f}")
            else:
                print("Received an invalid message format.")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server.")

async def send_requests(websocket):
    """Allow the user to send data requests to the server."""
    try:
        while True:
            user_input = input("Enter hex identifier to request (e.g., 0x01), or 'q' to quit: ")
            if user_input.lower() == 'q':
                break
            try:
                identifier = int(user_input, 16)
                if 0 <= identifier <= 0xFF:
                    message = struct.pack('!B', identifier)
                    await websocket.send(message)
                    print(f"Requested data for id=0x{identifier:02X}")
                else:
                    print("Identifier must be between 0x00 and 0xFF.")
            except ValueError:
                print("Invalid input. Please enter a valid hex value.")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server.")

async def main():
    """Establish connection to the server and start send/receive tasks."""
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websocket:
        print("Connected to the server.")
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_requests(websocket))
        done, pending = await asyncio.wait(
            [receive_task, send_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        print("Client tasks completed.")

asyncio.run(main())
