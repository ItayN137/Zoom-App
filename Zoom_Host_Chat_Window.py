import threading
import customtkinter
from PIL import Image, ImageTk
import tkinter
import socket
import tkinter.scrolledtext
import os


class ZoomHostChatWindow:
    def __init__(self):
        self._HOST = '127.0.0.1'
        self._PORT = 9091
        self.clients = []
        self.nicknames = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self._HOST, self._PORT))

        self.sock.listen()
        self.handle_receive()

    def handle_receive(self):
        while True:
            client, adress = self.sock.accept()
            #print(f"Connected with {str(adress)}!")

            client.send("NICKNAME".encode('utf-8'))
            nickname = client.recv(1024)

            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f"Name of client:{nickname}")
            self.broadcast(f"{nickname} connected to server!\n".encode('utf-8'))
            client.send("Connected to server!".encode('utf-8'))

            thread = threading.Thread(target=self.handle_message, args=(client,))
            thread.start()

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    # handle
    def handle_message(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                self.nicknames.remove(self.nicknames[index])
                break


ZoomHostChatWindow()

