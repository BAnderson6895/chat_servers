import asyncio
from datetime import datetime


class ConnectedUser:
    def __init__(self, address, user, reader, writer):
        self.address = address
        self.user = user
        self.reader = reader
        self.writer = writer

    def get_address(self):
        return self.address

    def get_user(self):
        return self.user


connected = []
latest_messages = []

PROTOCOL = "1"


async def send_protocol_to_client(reader, writer):
    message = "1"
    writer.write(message.encode())
    await writer.drain()


async def send_message(reader, writer, data):
    writer.write(data.encode())
    await writer.drain()


async def send_message_timestamped(reader, writer, data):
    data = datetime.now().strftime("%H:%M:%S") + " " + data
    await add_to_chat_history(data)
    writer.write(data.encode())
    await writer.drain()


async def receive_message(reader, writer):
    data = await reader.read(1024)
    message = data.decode()
    return message


async def add_to_chat_history(message):
    if len(latest_messages) == 10:
        latest_messages.pop(-1)
        latest_messages.append(message)
    else:
        latest_messages.append(message)


async def echo_chat(reader, writer):
    try:
        data = await reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')[0]

        if message == "1":
            await send_protocol_to_client(reader, writer)

        client_username = await receive_message(reader, writer)

        if len(connected) == 0:
            await send_message(reader, writer, "0")
        else:
            for client in connected:
                if client.user == client_username:
                    await send_message(reader, writer, "-1")
                else:
                    await send_message(reader, writer, "0")

        connected.append(ConnectedUser(addr, client_username, reader, writer))

        await receive_message(reader, writer)

        await send_message(reader, writer, str(latest_messages))

        while True:
            message = await receive_message(reader, writer)
            for client in connected:
                await send_message_timestamped(client.reader, client.writer, message)
    except OSError:
        for client in connected:
            if writer.get_extra_info('peername')[0] == client.address:
                print("Connection ended by user: " + client.user + ".")
                connected.remove(client)


async def main():
    try:
        server = await asyncio.start_server(echo_chat, '127.0.0.1', 8987)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()
    except KeyboardInterrupt as e:
        print(e)
if __name__ == '__main__':
    asyncio.run(main())
