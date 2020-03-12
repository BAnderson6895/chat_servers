import asyncio


async def match_protocol(reader, writer):
    client_protocol_num = "1"
    writer.write(client_protocol_num.encode())
    await writer.drain()

    server_protocol_num = await reader.read(1024)
    if server_protocol_num.decode() != "1":
        print(server_protocol_num.decode())
        print("1")
        return -1


async def receive_ten_latest_messages(reader, writer):
    data = await reader.read(1024)
    ten_messages = data.decode()
    message_list = ten_messages.strip('][').split(', ')
    for message in message_list:
        print(message)


async def send_message(reader, writer, data):
    data = data
    writer.write(data.encode())
    await writer.drain()


async def receive_message(reader, writer):
    data = await reader.read(1024)
    message = data.decode()
    return message


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('localhost', 8987)

    loop = asyncio.get_running_loop()

    response = await match_protocol(reader, writer)
    if response == -1:
        print("Client protocol version number does not match Server.")
        return

    username = input("Enter what you would like your username to be: ")
    await send_message(reader, writer, username)

    data = await reader.read(1)
    username_status = data.decode()
    if username_status == "-1":
        print("You cannot have the same username as another person on the server.")
        return
    await send_message(reader, writer, "continue")

    print("Ten latest messages:")
    await receive_ten_latest_messages(reader, writer)

    while True:
        chat = await loop.run_in_executor(None, input, username + ": ")
        chat = username + ": " + chat
        await send_message(reader, writer, chat)
        message = await receive_message(reader, writer)
        print(message)


def main():
    try:
        asyncio.run(tcp_echo_client())
    except KeyboardInterrupt:
        print("Quitting...")


if __name__ == '__main__':
    main()
