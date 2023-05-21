import customtkinter
import tkinter
from PIL import Image, ImageTk
import multiprocessing
import socket
import sys
import threading
import time
import multiprocessing
import tryclient
import tryserver
from tryclient import *
from tryserver import *


class ZoomClient:

    def __init__(self, username, ip_address):
        self._USERNAME = username
        self._IS_MUTED = True
        self._IS_CAMERA = False
        self._IS_SCREEN_SHARING = False
        self._CHAT_OPEN = False
        self._PARTICIPANTS_OPEN = False
        self._SETTINGS = False
        self._WIDTH = 1280
        self._HEIGHT = 920
        self.root = None
        self.lower_frame = None
        self.upper_frame = None
        self.label = None
        self.top_level = None
        self.app_image = None
        self.microphone_button = None
        self.camera_button = None
        self.share_screen_button = None
        self.chat_button = None
        self.participants_button = None
        self.settings_button = None
        self.window = None
        self.top_level_label = None
        self.muted_mic_image = customtkinter.CTkImage(light_image=Image.open("mute_microphone.png"),
                                                      dark_image=Image.open("mute_microphone.png"),
                                                      size=(20, 20))

        self.unmuted_mic_image = customtkinter.CTkImage(light_image=Image.open("microphone.png"),
                                                        dark_image=Image.open("microphone.png"),
                                                        size=(20, 20))

        self.camera_on = customtkinter.CTkImage(light_image=Image.open("video_camera.png"),
                                                dark_image=Image.open("video_camera.png"),
                                                size=(20, 20))

        self.camera_off = customtkinter.CTkImage(light_image=Image.open("no_video_camera.png"),
                                                 dark_image=Image.open("no_video_camera.png"),
                                                 size=(20, 20))

        self.share_screen_on_photo = customtkinter.CTkImage(light_image=Image.open("screen_share_on.png"),
                                                            dark_image=Image.open("screen_share_on.png"),
                                                            size=(20, 20))

        self.share_screen_off_photo = customtkinter.CTkImage(light_image=Image.open("screen_share_off.png"),
                                                             dark_image=Image.open("screen_share_off.png"),
                                                             size=(20, 20))

        self.chat_photo = customtkinter.CTkImage(light_image=Image.open("chat.png"),
                                                 dark_image=Image.open("chat.png"),
                                                 size=(20, 20))

        self.participants_photo = customtkinter.CTkImage(light_image=Image.open("group.png"),
                                                         dark_image=Image.open("group.png"),
                                                         size=(20, 20))
        self.settings_photo = customtkinter.CTkImage(light_image=Image.open("settings.png"),
                                                     dark_image=Image.open("settings.png"),
                                                     size=(20, 20))

        self.screen_default_photo = customtkinter.CTkImage(light_image=Image.open("black_screen.png"),
                                                           dark_image=Image.open("black_screen.png"),
                                                           size=(1200, 600))

        self.camera_default_photo = customtkinter.CTkImage(light_image=Image.open("black_screen.png"),
                                                           dark_image=Image.open("black_screen.png"),
                                                           size=(1200, 200))

        self.audio_client = tryclient.MicrophoneAudioClient(ip_address)
        self.screen_share_client = tryclient.ScreenShareClient(ip_address)
        self.camera_client = tryclient.CameraClient(ip_address)

        threading.Thread(target=self.handle_new_client).start()

    def handle_new_client(self):
        self.root = customtkinter.CTk()
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.root.title("Itay's Zoom Application")

        self.app_image = tkinter.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)

        self.label = customtkinter.CTkLabel(master=self.root, text="Itay's Zoom Application",
                                            font=("Arial", 25))
        self.label.pack(pady=6, padx=5)

        self.camera_display_label = customtkinter.CTkLabel(master=self.root, image=self.camera_default_photo, text="")
        self.camera_display_label.place(relx=0.5, rely=0.16, anchor=tkinter.CENTER)

        self.screen_display_label = customtkinter.CTkLabel(master=self.root, image=self.screen_default_photo, text="")
        self.screen_display_label.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

        self.lower_frame = customtkinter.CTkFrame(master=self.root, width=400, height=50)
        self.lower_frame.pack(ipadx=400, ipady=4, side="bottom")

        self.microphone_button = customtkinter.CTkButton(master=self.lower_frame, image=self.muted_mic_image,
                                                         text="Unmute",
                                                         font=("Ariel", 15, "bold"), width=10, height=10,
                                                         command=self.handle_mic)
        self.microphone_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.camera_button = customtkinter.CTkButton(master=self.lower_frame, image=self.camera_off,
                                                     text="Turn On",
                                                     font=("Ariel", 15, "bold"), width=10, height=10,
                                                     command=self.handle_camera)
        self.camera_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.share_screen_button = customtkinter.CTkButton(master=self.lower_frame, image=self.share_screen_off_photo,
                                                           text="Share Screen",
                                                           font=("Ariel", 15, "bold"), width=10, height=10,
                                                           command=self.handle_share_screen)
        self.share_screen_button.pack(pady=10, padx=10, side="left", anchor=tkinter.CENTER)

        self.chat_button = customtkinter.CTkButton(master=self.lower_frame, image=self.chat_photo,
                                                   text="Chat",
                                                   font=("Ariel", 15, "bold"), width=10, height=10,
                                                   command=self.handle_chat())
        self.chat_button.pack(pady=10, padx=10, side="right", anchor=tkinter.CENTER)

        self.participants_button = customtkinter.CTkButton(master=self.lower_frame, image=self.participants_photo,
                                                           text="Participants",
                                                           font=("Ariel", 15, "bold"), width=10, height=10,
                                                           command=self.handle_participants())
        self.participants_button.pack(pady=10, padx=10, side="right", anchor=tkinter.CENTER)

        threading.Thread(target=self.audio_client.start).start()

        self.camera_display_label.after(0, self.camera_client.start, self.camera_display_label)

        self.screen_display_label.after(0, self.screen_share_client.start, self.screen_display_label)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_close)
        self.root.mainloop()

    def confirm_close(self):
        if askyesno(title='Exit', message='Close Window?'):
            self.screen_share_client.stop_stream()
            self.screen_share_client.exit_window()
            self.audio_client.stop_mic()
            self.audio_client.exit_window()
            self.camera_client.stop_stream()
            self.camera_client.exit_window()
            sys.exit()

    def handle_mic(self):
        """
        handle the press of the button. changes the button to mute or un-mute text and image and also provides
        the audio share between clients
        :return:
        """
        if self._IS_MUTED:
            self._IS_MUTED = False
            self.microphone_button.configure(image=self.unmuted_mic_image, text="Mute",
                                             font=("Ariel", 15, "bold"), width=10, height=10)
            self.audio_client.start_mic()

        else:
            self._IS_MUTED = True
            self.microphone_button.configure(image=self.muted_mic_image,
                                             text="Unmute",
                                             font=("Ariel", 15, "bold"), width=10, height=10)
            self.audio_client.stop_mic()
        return

    def handle_camera(self):
        """
        handle the press of the button. changes the button to camera on or off with text and image and also provides
        the camera share between clients
        :return:
        """
        if not self._IS_CAMERA:
            self._IS_CAMERA = True
            self.camera_button.configure(image=self.camera_on,
                                         text="Turn Off",
                                         font=("Ariel", 15, "bold"), width=10, height=10)
            self.camera_client.start_stream()

        else:
            self._IS_CAMERA = False
            self.camera_button.configure(image=self.camera_off,
                                         text="Turn On",
                                         font=("Ariel", 15, "bold"), width=10, height=10)
            self.camera_client.stop_stream()

        return

    def handle_share_screen(self):
        """
        handle the press of the button. changes the button to share screen on or off with text and image and also
        provides the screen share between clients
        :return:
        """
        if not self._IS_SCREEN_SHARING:
            self._IS_SCREEN_SHARING = True
            self.share_screen_button.configure(image=self.share_screen_on_photo,
                                               text="Stop Sharing",
                                               font=("Ariel", 15, "bold"), width=10, height=10)
            self.screen_share_client.start_stream()
        else:
            self._IS_SCREEN_SHARING = False
            self.share_screen_button.configure(image=self.share_screen_off_photo,
                                               text="Share Screen",
                                               font=("Ariel", 15, "bold"), width=10, height=10)
            self.screen_share_client.stop_stream()
        return

    def handle_chat(self):
        """
        handle the press of the button. opening and closing the chat window
        :return:
        """
        if not self._CHAT_OPEN:
            self._CHAT_OPEN = True
            # open the chat window
        else:
            self._CHAT_OPEN = False
            # close the chat window
        return

    def handle_participants(self):
        """
        handle the press of the button. opening and closing the participants window
        :return:
        """
        if not self._PARTICIPANTS_OPEN:
            self._PARTICIPANTS_OPEN = True
            # open the participants window
        else:
            self._PARTICIPANTS_OPEN = False
            # close the participants window
        return


class HostZoomClient(ZoomClient):

    def __init__(self, name, kick_adminstartion):
        tryserver.AudioServer().start()
        tryserver.ScreenStreamingServer().start()
        tryserver.CameraStreamingServer().start()
        super().__init__(name, kick_adminstartion)


def main():
    client = HostZoomClient("Itay", socket.gethostname())


if __name__ == '__main__':
    main()
