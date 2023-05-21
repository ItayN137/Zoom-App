import threading
import sys
import customtkinter
from PIL import Image, ImageTk
import tkinter
import socket
import tkinter.scrolledtext
import os


class ChatWindow:
    def __init__(self, client_name, ip_of_host, port_of_host):
        self._CLIENT_NAME = client_name
        self._IP = ip_of_host
        self._PORT = port_of_host
        self._WIDTH = 350
        self._HEIGHT = 500
        self.root = 0
        self.lower_frame = 0
        self.upper_frame = 0
        self.send_button = 0
        self.sock = 0
        self.app_image = 0
        self.label = 0
        self.input_area = 0
        self.text_area = 0
        self.gui_done = False
        self.running = True
        self.send_photo = customtkinter.CTkImage(light_image=Image.open("send.png"),
                                                 dark_image=Image.open("send.png"),
                                                 size=(20, 20))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self._IP, self._PORT))

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.handle_receive)

        gui_thread.start()
        receive_thread.start()




    def gui_loop(self):
        self.root = customtkinter.CTk()
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.root.title("Itay's Zoom Application")

        self.app_image = tkinter.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)

        self.label = customtkinter.CTkLabel(master=self.root, text="Itay's Zoom Application",
                                            font=("Arial", 25))
        self.label.pack(pady=6, padx=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.root)
        self.text_area.pack(padx=20, pady=5, side="top", anchor=tkinter.CENTER)
        self.text_area.config(state='disabled')

        self.send_button = customtkinter.CTkButton(master=self.root, image=self.send_photo,
                                                   text="",
                                                   font=("Ariel", 15, "bold"), width=10, height=10,
                                                   command=self.handle_send)
        self.send_button.pack(pady=10, padx=10, side="right", anchor=tkinter.S)

        self.input_area = tkinter.Text(self.root, height=2)
        self.input_area.pack(padx=20, pady=5, side="bottom", anchor=tkinter.CENTER)

        self.gui_done = True
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

        self.root.mainloop()

    def handle_send(self):
        message = f"{self._CLIENT_NAME}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.root.destroy()
        self.sock.close()
        sys.exit()

    def handle_receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICKNAME':
                    self.sock.send(self._CLIENT_NAME.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state="normal")
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


def main():
    cw = ChatWindow("Itay", '127.0.0.1', 9091)


if __name__ == '__main__':
    main()
