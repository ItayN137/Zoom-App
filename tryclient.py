import socket
import sys
import threading
from io import BytesIO
import tkinter as tk

import customtkinter
import customtkinter as Ctk
import cv2
import pyaudio
from PIL import ImageGrab, Image, ImageTk, JpegImagePlugin
import io
import time
from pynput.mouse import Controller
from Window import Window
from abc import ABC
import soundcard as sc
from tkinter.messagebox import askyesno


class Client(ABC):

    def __init__(self, ip_address):
        self.host = ip_address
        self.port = None
        self.server_address = None

        self.__running = False

    def connect_udp_socket(self):
        # Open a socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, data):
        """Gets encoded data to send"""
        self.server_socket.sendto(data, self.server_address)

    def exit_window(self):
        sys.exit()


class StreamingClient(Client):

    def __init__(self, ip_address):
        super().__init__(ip_address)
        self.__stream_on = False
        self.root = None
        self.app_image = None
        self.label = None
        self.server_socket = None
        self.window = None
        self.func = None

        self.cursor = Image.open("cursor.png").resize((28, 28))
        self.my_cursor = Controller()

        # Connect to udp server
        self.connect_udp_socket()

    def send_screenshot(self):
        """Function to send the screenshot"""

        previous_screenshot = None
        bio = io.BytesIO()
        image_quality = 10

        while True:
            print(f"Status: {self.__stream_on} on port: {self.port}")
            if self.__stream_on:
                # Take a screenshot of the monitor or the camera
                screenshot = self.get_frame()
                if previous_screenshot == screenshot:
                    continue

                # Saving the photo to the digital storage
                screenshot.save(bio, "JPEG", quality=image_quality)
                bio.seek(0)

                # Getting the bytes of the photo
                screenshot = bio.getvalue()

                # Restarting the storage
                bio.truncate(0)

                length = len(screenshot)
                if length < 65000:
                    # Sending the screenshot
                    self.send_message(screenshot)
                    if image_quality < 90 and length < 65000:
                        image_quality += 5
                else:
                    image_quality -= 10
                previous_screenshot = screenshot

    def receive_screenshot(self):
        """Function to receive and display the screenshot"""
        previous_img = None

        while True:
            try:
                # Receive the screenshot from the server
                screenshot_bytes, server_address = self.server_socket.recvfrom(65000)

                # Create a PhotoImage object from the received data
                screenshot = Image.open(BytesIO(screenshot_bytes))
                img = ImageTk.PhotoImage(screenshot)

                # Update the label with the new screenshot
                if not previous_img == img:
                    self.update_label(self.label, img)
                previous_img = img
            except:
                continue

    def update_label(self, label, img):
        """updating label with given image"""
        if type(img) == JpegImagePlugin.JpegImageFile:
            img = ImageTk.PhotoImage(img)

        label.configure(image=img)
        label.update()
        return

    def start(self, label):
        # Setting the label to update
        self.label = label

        # Send screenshots to the server
        threading.Thread(target=self.send_screenshot).start()

        time.sleep(1 / 3)

        threading.Thread(target=self.receive_screenshot).start()

    def start_stream(self):
        self.__stream_on = True
        return

    def stop_stream(self):
        self.__stream_on = False
        self.send_message("Q".encode())
        return

    def get_frame(self):
        pass

    def confirm_close(self):
        self.send_message("Q".encode())
        self.__stream_on = False
        self.server_socket.close()
        self.window.destroy()
        sys.exit()


class ScreenShareClient(StreamingClient):

    def __init__(self, ip_address):
        super(ScreenShareClient, self).__init__(ip_address)
        self.port = 12343
        self.server_address = (self.host, self.port)

    def get_frame(self):
        frame = ImageGrab.grab()

        # Drawing a mouse on the screen
        frame = frame.convert("RGBA")
        frame.alpha_composite(self.cursor, dest=self.my_cursor.position)
        frame = frame.convert("RGB")

        # Resizing the photo
        frame = frame.resize((1200, 600))

        return frame


class CameraClient(StreamingClient):

    def __init__(self, ip_address, x_res=1280, y_res=720):
        super(CameraClient, self).__init__(ip_address)
        self.port = 12344
        self.server_address = (self.host, self.port)
        self.__x_res = x_res
        self.__y_res = y_res
        self.__camera = cv2.VideoCapture(0)
        self.__configure()

    def __configure(self):
        self.__camera.set(3, self.__x_res)
        self.__camera.set(4, self.__y_res)

    def get_frame(self):
        # Get the screenshot from webcam
        ret, frame = self.__camera.read()

        # Convert screenshot to PIL image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        # Resizing the photo
        pil_image = pil_image.resize((300, 200))

        return pil_image


class AudioClient(Client):

    def __init__(self, ip_address):
        super().__init__(ip_address)
        self.server_socket = None
        self.stream = None
        self.__muted = True

        # Private Parameters
        self._chunk = 1024
        self._format = pyaudio.paInt16
        self._channels = 1
        self._rate = 44100

        self.port = 12345
        self.server_address = (self.host, self.port)

        # Connect to udp server
        self.connect_udp_socket()

        # Create a PyAudio object
        self.audio = pyaudio.PyAudio()

        # Create a PyAudio stream for playback
        self.stream = self.audio.open(format=self._format, channels=self._channels,
                                      rate=self._rate, input=True, frames_per_buffer=self._chunk)

        self.speaker = self.audio.open(format=self._format, channels=self._channels,
                                       rate=self._rate, output=True)

    def recv_data(self):
        while True:
            try:
                # Receive a chunk of audio data from a client
                data, address = self.server_socket.recvfrom(65000)

                # Play back audio data
                self.speaker.write(data)
            except:
                continue

    def send_data(self):
        # Loop forever and send audio data to the server
        while True:
            print(f"Audio: {self.__muted}")
            if not self.__muted:
                # Read a chunk of audio data from the microphone
                data = self.get_audio_data()

                # Send the audio data to the server
                self.send_message(data)

    def start(self):
        threading.Thread(target=self.send_data).start()

        time.sleep(1 / 3)

        threading.Thread(target=self.recv_data).start()

    def start_mic(self):
        self.__muted = False
        return

    def stop_mic(self):
        self.__muted = True
        return

    def get_audio_data(self):
        pass


class MicrophoneAudioClient(AudioClient):

    def __init__(self, ip_address):
        super(MicrophoneAudioClient, self).__init__(ip_address)
        self._rate = 16000

    def get_audio_data(self):
        return self.stream.read(self._chunk)


class ComputerAudioClient(AudioClient):

    def __init__(self):
        super(ComputerAudioClient, self).__init__()
        self._rate = 8000

    def get_audio_data(self):
        default_speaker = sc.default_speaker()
        with sc.get_microphone(str(default_speaker.id),
                               include_loopback=True).recorder(samplerate=self._rate) as mic:
            data = mic.record(numframes=self._rate)
            print(len(data))
            print(len(data.tobytes()))
        return data

    def recv_data(self):
        response = b''
        while True:
            while True:
                # Receive a chunk of audio data from a client
                data, address = self.server_socket.recvfrom(65000)
                if not data:
                    break
                response += data

            # Play back audio data
            self.speaker.write(response)

    def send_data(self):
        # Loop forever and send audio data to the server
        while True:
            # Read a chunk of audio data from the microphone
            data = self.get_audio_data()

            # Split th data every 50,000 bytes
            num_channels = data.shape[1]
            bytes_per_sample = data.dtype.itemsize
            max_chunk_size = int((65000 // num_channels) // bytes_per_sample)
            chunks = [data[i:i + max_chunk_size] for i in range(0, len(data), max_chunk_size)]

            # Send the audio data to the server
            for chunk in chunks:
                print(len(chunk.tobytes()))
                self.send_message(chunk.tobytes())


def main():
    c = ScreenShareClient()

    root = customtkinter.CTk()
    window = Window(root)
    root = window.create_tk_window()
    label = window.create_label(master=root)

    label.after(0, c.start, label)

    root.mainloop()

    # c = MicrophoneAudioClient()
    # c.start()
    # c.start_mic()



if __name__ == '__main__':
    main()