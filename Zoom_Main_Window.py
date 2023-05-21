import sys
import threading
from tkinter.messagebox import askyesno
import sqlite3
import customtkinter
from PIL import Image, ImageTk
import tkinter

import Zoom_Client
from Zoom_Client import ZoomClient, HostZoomClient


class Zoom_Main_Window:

    def __init__(self):
        self.root = None
        self.frame = None
        self.label = None
        self.entry1 = None
        self.entry2 = None
        self.entry3 = None
        self.create_button = None
        self.join_button = None
        self.__meeting_id = None
        self.__meeting_password = None
        self.__username = None

        self.build_data_base()

        threading.Thread(target=self.handle_zoom_window).start()

    def build_connection_to_db(self):
        # Build the database file + the control tool of it
        db_connection = sqlite3.connect("servers.db")
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor

    def build_data_base(self):
        db_connection, db_cursor = self.build_connection_to_db()
        db_cursor.execute("""CREATE TABLE IF NOT EXISTS servers (
                                    ip int,
                                    password VARCHAR(255) NOT NULL
                                )""")

        # Running the command
        db_connection.commit()

    def handle_zoom_window(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.root = customtkinter.CTk()
        self.root.geometry("300x400")
        self.root.title("Itay's Zoom Application")

        self.app_image = tkinter.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)

        self.label = customtkinter.CTkLabel(master=self.root, text="Itay's Zoom Application", font=("Arial", 25))
        self.label.pack(pady=12, padx=10)

        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Username")
        self.entry1.pack(pady=12, padx=10)

        self.entry2 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Meeting ID")
        self.entry2.pack(pady=12, padx=10)

        self.entry3 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Password")
        self.entry3.pack(pady=12, padx=10)

        self.create_button = customtkinter.CTkButton(master=self.frame, text="Create New Meeting",
                                                     command=self.handle_new_host_client)
        self.create_button.pack(pady=12, padx=10)

        self.join_button = customtkinter.CTkButton(master=self.frame, text="Join Meeting",
                                                   command=self.handle_new_client)
        self.join_button.pack(pady=12, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_close)
        self.root.mainloop()

    def handle_new_client(self):
        self.__username = self.entry1.get()
        self.__meeting_id = self.entry2.get()
        self.__meeting_password = self.entry3.get()

        if not self.validate_entry(self.__username, self.__meeting_id, self.__meeting_password):
            if self.check_db(self.__meeting_id, self.__meeting_password):
                Zoom_Client.ZoomClient(self.__username, self.__meeting_id)
            else:
                self.create_top_level("IP Address not found, try again!")
        else:
            self.create_top_level("One or more fields are empty, try again!")
            return

    def handle_new_host_client(self):
        self.__username = self.entry1.get()
        self.__meeting_id = self.entry2.get()
        self.__meeting_password = self.entry3.get()

        if not self.validate_entry(self.__username, self.__meeting_id, self.__meeting_password):
            # encrypted_password = encrypt(self.__meeting_password)
            # self.inject_to_db( self.__meeting_id, encrypted_password)
            Zoom_Client.HostZoomClient(self.__username, self.__meeting_id)
        else:
            self.create_top_level("One or more fields are empty, try again!")
            return

    def validate_entry(self, *args):
        for arg in args:
            if arg == "":
                return True
        return False

    def check_db(self, ip, password):
        db_connection, db_cursor = self.build_connection_to_db()
        db_cursor.execute(f"SELECT password FROM servers WHERE ip={ip}")
        #password = encrypt()
        encrypted_password = db_cursor.fetchall()
        return password == encrypted_password

    def create_top_level(self, text):
        top_level = customtkinter.CTkToplevel()
        top_level.geometry("500x50")
        top_level.title("Itay's Zoom Application")
        top_level.iconphoto(False, self.app_image)
        label = customtkinter.CTkLabel(master=top_level, text=text, font=("Ariel", 20, "bold"), width=10, height=10)
        label.pack(pady=10, padx=10, anchor=tkinter.CENTER)


    def confirm_close(self):
        if askyesno(title='Exit', message='Close Window?'):
            sys.exit()


def main():
    zoom1 = Zoom_Main_Window()


if __name__ == '__main__':
    main()
