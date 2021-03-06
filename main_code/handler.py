import glob
import tkinter as tk
import pyaudio
import wave
from tkinter import Button, Frame, Label, Tk, Listbox
import threading
from main_code.fourier import calc_and_plot_xcorr_dft_with_ground_truth
from main_code.codification_signals import enconding_man_diff
from main_code.codification_signals import analog_to_digital_converter
import matplotlib.pyplot as plt
import scipy.io.wavfile as waves
import numpy as np


class AnalizerEncoderSound:
    # Static variables
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    CHUNK = 1024
    RECORDING_TIME_SECONDS = 5

    def __init__(self, window: Tk) -> None:
        # Variables
        self.seconds_counter = 0
        self.process_timer = None

        window.title('Sound analyzer and encoder')
        window.geometry("800x300")

        # CREATION FRAMES
        main_frame = Frame(
            window,
            background="#c4ceff",
            borderwidth=5,
            relief="groove"
        )
        main_frame.pack(
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
            expand=True,
            fill=tk.BOTH,
        )
        frame_1_2 = Frame(
            main_frame,
            background="#c8ffa6",
            borderwidth=2,
            relief="ridge"
        )
        frame_1_2.place(
            relx=0.01,
            rely=0.01,
            relwidth=0.59,
            relheight=0.97
        )
        frame1 = Frame(
            frame_1_2,
            background="#c8ffa6",
            borderwidth=2,
            relief="ridge"
        )
        frame1.pack(
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
            expand=True,
            fill=tk.BOTH,
        )
        frame2 = Frame(
            frame_1_2,
            background="#c8ffa6",
            borderwidth=2,
            relief="ridge"
        )
        frame2.pack(
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
            expand=True,
            fill=tk.BOTH,
        )
        frame3 = Frame(
            main_frame,
            background="#c8ffa6",
            borderwidth=2,
            relief="ridge"
        )
        frame3.place(
            relx=0.61,
            rely=0.01,
            relwidth=0.38,
            relheight=0.97
        )

        # LABELS
        self.time = Label(
            frame1,
            fg='green',
            text="00",
            bg="black",
            font=("", "18")
        )
        self.time.pack(
            padx=5,
            pady=5,
            side=tk.TOP,
            expand=True,
            fill=tk.BOTH
        )
        self.status_recording = Label(
            frame1,
            fg='white',
            text="Not started",
            bg="gray",
            font=("", "13")
        )
        self.status_recording.pack(
            padx=5,
            pady=5,
            side=tk.TOP,
            expand=True,
            fill=tk.BOTH
        )

        # BUTTONS
        self.btn_start = Button(
            frame1,
            fg='blue',
            width=16,
            text='Record sound',
            command=self.start_execution
        )
        self.btn_start.pack(
            padx=5,
            pady=5,
            side=tk.RIGHT,
            expand=True,
            fill=tk.BOTH
        )
        self.btn_fourier = Button(
            frame2,
            fg='blue',
            width=16,
            text='Fourier Analysis',
            command=self.fourier_analysis
        )
        self.btn_fourier.pack(
            padx=5,
            pady=5,
            side=tk.LEFT,
            expand=True,
            fill=tk.BOTH
        )
        self.btn_graphs_single = Button(
            frame2,
            fg='blue',
            width=16,
            text='Simple charts',
            command=self.simple_charts
        )
        self.btn_graphs_single.pack(
            padx=5,
            pady=5,
            side=tk.LEFT,
            expand=True,
            fill=tk.BOTH
        )
        self.btn_dtd = Button(
            frame2,
            fg='blue',
            width=16,
            text='Digital to Digital',
            command=self.digital_to_digital
        )
        self.btn_dtd.pack(
            padx=5,
            pady=5,
            side=tk.LEFT,
            expand=True,
            fill=tk.BOTH
        )
        self.btn_refresh_listbox = Button(
            frame3,
            fg='blue',
            width=16,
            text='Refresh list of audio files',
            command=self.read_audio_files
        )
        self.btn_refresh_listbox.pack(
            padx=5,
            pady=5,
            expand=True,
            fill=tk.X
        )

        # LISTBOX
        self.list_udio_files = Listbox(frame3)
        self.list_udio_files.pack(
            padx=5,
            pady=5,
            expand=True,
            fill=tk.X
        )

    def start_execution(self):
        self.btn_start.config(state='disabled')
        rec_sound_thread = threading.Thread(target=self.record_sound)
        count_time_thread = threading.Thread(target=self.chronometer)
        rec_sound_thread.start()
        count_time_thread.start()

    def record_sound(self):
        audio = pyaudio.PyAudio()
        archivo = "grabacion.wav"
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        frames = []

        print("recording.....")
        self.status_recording['text'] = "recording....."
        for _ in range(0, int(self.RATE / self.CHUNK * self.RECORDING_TIME_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        self.status_recording['text'] = ".....recording finished"
        print(".....recording finished")

        # Ajustamos los controloes de cronometro
        self.btn_start.config(state='normal')
        self.time.after_cancel(self.process_timer)
        self.time['text'] = "00"
        self.seconds_counter = 0

        # DETENEMOS GRABACI??N
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
        recordings = glob.glob('*.wav')
        count = 0
        for i in recordings:
            if "grabacion" in i:
                count += 1
        if count > 0:
            archivo = "grabacion"+"("+str(count)+")"+".wav"

        waveFile = wave.open(archivo, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

    def chronometer(self):
        self.time['text'] = str(self.seconds_counter)
        self.seconds_counter += 1
        self.process_timer = self.time.after(1000, self.chronometer)

    def fourier_analysis(self):
        self.btn_start.config(state='disabled')
        self.run_analysis()
        self.btn_start.config(state='normal')

    def run_analysis(self):
        lines = self.list_udio_files.size()
        signal_composite = np.ndarray([])
        for i in range(lines):
            file_sound = self.list_udio_files.get(i)
            _, data = waves.read(file_sound)
            signal_composite = signal_composite+data[:-800, 0]

        calc_and_plot_xcorr_dft_with_ground_truth(
            signal_composite,
            800,
            time_domain_graph_title="Sounds loaded: 5 seconds"
        )
        plt.show()

    def read_audio_files(self):
        lines = self.list_udio_files.size()
        self.list_udio_files.delete(0, lines)
        recordings = glob.glob('*.wav')
        for i, value in enumerate(recordings):
            self.list_udio_files.insert(i+1, value)

    def simple_charts(self):
        signal_composite = np.ndarray([])

        lines = self.list_udio_files.size()
        _, ax = plt.subplots(lines+1, 1, sharex='col', figsize=(10, 16))
        plt.suptitle("Original signals")
        for i in range(lines):
            file_sound = self.list_udio_files.get(i)
            _, data = waves.read(file_sound)
            audio_data = data[:-800, 0]
            ax[i].plot(audio_data)
            ax[i].set_title(file_sound)
            signal_composite = signal_composite+audio_data

        ax[lines].plot(signal_composite, color="g")
        ax[lines].set_title('Sum of all signals')
        plt.axhline(0, color='black')

        plt.show()

    def digital_to_digital(self):
        lines = self.list_udio_files.size()
        signal_composite = np.ndarray([])
        for i in range(lines):
            file_sound = self.list_udio_files.get(i)
            _, data = waves.read(file_sound)
            signal_composite = signal_composite+data[:-800, 0]

        new_signal = analog_to_digital_converter(signal_composite, 20, 5)

        L = 32  # number of digital samples per data bit
        voltage_level = 20  # peak voltage level in Volts
        data1 = new_signal[0]
        clk = np.arange(0, 2*len(data1)) % 2  # clock samples

        man_diff1 = enconding_man_diff(clk, data1)

        manchesterdiff_seq = np.repeat(man_diff1, L)
        clk_seq = np.repeat(clk, L)
        data_seq = np.repeat(data1, 2*L)

        _, ax = plt.subplots(3, 1, sharex='col', figsize=(10, 14))
        ax[0].plot(clk_seq)
        ax[0].set_title('Clocking')
        ax[1].plot(data_seq)
        ax[1].set_title('Digital Data')
        ax[2].plot(manchesterdiff_seq)
        ax[2].set_title('Manchester Differential')

        plt.show()
