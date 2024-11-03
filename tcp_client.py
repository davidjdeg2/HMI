# tcp_client.py
import asyncio
import socket
import struct

# Mapping of hex identifiers to parameter names
identifier_mapping = {
    0x01: 'battery_soc',
    0x02: 'temperature',
    # You can add more mappings here
}

async def receive_messages(reader):
    """Listen for incoming messages from the TCP server and process them."""
    try:
        while True:
            # Read exactly 5 bytes (1 byte for identifier + 4 bytes for float)
            message = await reader.readexactly(5)
            if len(message) == 5:
                identifier, value = struct.unpack('!Bf', message)
                parameter_name = identifier_mapping.get(identifier, f"Unknown(0x{identifier:02X})")
                print(f"Received: {parameter_name} = {value:.2f}")
            else:
                print("Received an invalid message format.")
    except asyncio.IncompleteReadError:
        print("Connection closed by the server.")

async def send_requests(writer):
    """Allow the user to send data requests to the TCP server."""
    try:
        while True:
            user_input = input("Enter hex identifier to request (e.g., 0x01), or 'q' to quit: ")
            if user_input.lower() == 'q':
                break
            try:
                identifier = int(user_input, 16)
                if 0 <= identifier <= 0xFF:
                    message = struct.pack('!B', identifier)
                    writer.write(message)
                    await writer.drain()
                    print(f"Requested data for id=0x{identifier:02X}")
                else:
                    print("Identifier must be between 0x00 and 0xFF.")
            except ValueError:
                print("Invalid input. Please enter a valid hex value.")
    except ConnectionResetError:
        print("Connection closed by the server.")

async def main():
    """Establish TCP connection to the server and start send/receive tasks."""
    host = 'localhost'
    port = 8765

    # Establish connection using asyncio's streams
    reader, writer = await asyncio.open_connection(host, port)
    print("Connected to the TCP server.")

    # Start tasks for sending and receiving messages
    receive_task = asyncio.create_task(receive_messages(reader))
    send_task = asyncio.create_task(send_requests(writer))

    # Wait for either task to complete
    done, pending = await asyncio.wait(
        [receive_task, send_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel remaining tasks and close the connection
    for task in pending:
        task.cancel()
    writer.close()
    await writer.wait_closed()
    print("Client tasks completed.")

# Entry point for the asyncio loop
if __name__ == "__main__":
    asyncio.run(main())
