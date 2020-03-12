import socket
from threading import Thread
import os
import time
from datetime import datetime
import queue


PORT = 9999


def chatMessage():
    # handler of chat messages
    global username
    global broadcastSocket
    global currentOnline
    global chatHistory

    while True:
        receivedMessage = broadcastSocket.recv(1024)
        receivedMessageInString = str(receivedMessage.decode('utf-8'))
        if receivedMessageInString.find(':') != -1:
            print('\r%s\n' % receivedMessageInString, end='')
        elif receivedMessageInString.find('!@#') != -1 and receivedMessageInString.find(':') == -1 \
                and receivedMessageInString[3:] in currentOnline:
            currentOnline.remove(receivedMessageInString[3:])
            print('*************************************************')
            print('********           chat history          ********')
            for item in list(chatHistory.queue):
                print(item, end="\n")
            print('*************************************************')
            print('<<system>> ' + username + ' connected.')
            print('<<system>> Currently online: ' + str(len(currentOnline)))
        elif not (receivedMessageInString in currentOnline) and receivedMessageInString.find(':') == -1:
            currentOnline.append(receivedMessageInString)
            print('*************************************************')
            print('********           chat history          ********')
            for item in list(chatHistory.queue):
                print(item, end="\n")
            print('*************************************************')
            print('<<system>> ' + username + ' connected.')
            print('<<system>> Currently online: ' + str(len(currentOnline)))


def statusBroadcast():
    # broadcast online status of peers
    global username
    global sendSocket

    while True:
        time.sleep(1)
        sendSocket.sendto(username.encode('utf-8'), ('255.255.255.255', 9999))


def chatBroadcast():
    # broadcast chat messages
    global username
    global sendSocket
    global currentOnline
    global chatHistory
    chatHistory = queue.Queue()

    while True:
        # broadcast input message to chat room
        # provide exit command
        data = input()
        if data == 'cquit':
            closeMessage = '<<system>>' + ' ' + username + ' disconnected at ' + datetime.now().strftime("%H:%M:%S")
            sendSocket.sendto(closeMessage.encode('utf-8'), ('255.255.255.255', 9999))
            print('<<system>> Currently online: ' + str(len(currentOnline)))
            os._exit(1)
        if data == 'hist':
            print('*************************************************')
            print('********           chat history          ********')
            for item in list(chatHistory.queue):
                print(item, end="\n")
            print('*************************************************')
        elif data != '' and data != 'cquit':
            sendMessage = datetime.now().strftime("%H:%M:%S") + " " + username + ': ' + data
            sendSocket.sendto(sendMessage.encode('utf-8'), ('255.255.255.255', 9999))
            chatHistory.put(sendMessage.encode('utf-8'))
        else:
            print('<<system>> Write a message first!')


def main():
    global currentOnline
    global receiveThread
    global sendThread
    global statusThread
    global broadcastSocket
    global sendSocket
    global username
    username = ''

    print('*************************************************')
    print('*              p2p chat program                 *')
    print('*        type cquit to close program            *')
    print('*        type hist to get chat history          *')
    print('*************************************************')

    # get username input from user
    # if no username is entered prompt this again
    while True:
        if not username:
            username = input('<<system>> Please enter a nickname: ')
            if not username:
                print('<<system>> Enter a nickname first!')
            else:
                break

    print('*************************************************')

    broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcastSocket.bind(('0.0.0.0', 9999))

    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    currentOnline = []
    receiveThread = Thread(target=chatMessage)
    sendThread = Thread(target=chatBroadcast)
    statusThread = Thread(target=statusBroadcast)

    receiveThread.start()
    sendThread.start()
    statusThread.start()

    receiveThread.join()
    sendThread.join()
    statusThread.join()


if __name__ == '__main__':
    main()
