import glob
import pyaudio
import wave
from tkinter import Button, Frame, Label, Tk, Listbox
import threading
from makelab import signal
from main_code.fourier import calc_and_plot_xcorr_dft_with_ground_truth
import matplotlib.pyplot as plt
import scipy.io.wavfile as waves


class AnalizerEncoderSound:
    def __init__(self, window: Tk) -> None:
        # Variables
        self.recording = False
        self.seconds_counter = 0
        self.process_timer = None

        window.title('Sound analyzer and encoder')
        window.geometry("700x300")

        main_frame = Frame(window)
        main_frame.pack(padx=5, pady=5)

        frame1 = Frame(main_frame, padx=5, pady=5)
        frame1.pack()

        frame2 = Frame(main_frame, padx=5, pady=5)
        frame2.pack()

        frame3 = Frame(main_frame, padx=5, pady=5)
        frame3.pack()

        # Etiquetas
        self.time = Label(
            frame1,
            fg='green',
            width=15,
            text="00",
            bg="black",
            font=("", "30")
        )
        self.time.pack()
        self.status_recording = Label(
            frame1,
            fg='white',
            width=20,
            text="Not started",
            bg="gray",
            font=("", "15")
        )
        self.status_recording.pack()
        title_list = Label(
            frame3,
            text="List of audio files",
        )
        title_list.pack()

        # BOTONES
        self.btn_start = Button(frame2, fg='blue', width=16,
                                text='Grabar', command=self.start_execution)
        self.btn_start.grid(row=0, column=0)

        self.btn_stop = Button(frame2, fg='blue', width=16,
                               text='Parar', command=self.stop_recording)
        self.btn_stop.grid(row=0, column=1)

        self.btn_fourier = Button(frame2, fg='blue', width=16,
                                  text='Fourier Analysis', command=self.fourier_analysis)
        self.btn_fourier.grid(row=0, column=2)

        # listbox
        self.list_udio_files = Listbox(frame3,)
        self.list_udio_files.pack()

    def run_analysis(self):
        file_sound = self.list_udio_files.get(0)
        samplerate, data = waves.read(file_sound) 
        Audio_m = data[:,0]

        sampling_rate = 800
        total_time_in_secs = 0.5
        freq1 = 10
        freq2 = 42
        freq3 = 151
        signal1 = signal.create_sine_wave(
            freq1, sampling_rate, total_time_in_secs)
        signal2 = signal.create_sine_wave(
            freq2, sampling_rate, total_time_in_secs)
        signal3 = signal.create_sine_wave(
            freq3, sampling_rate, total_time_in_secs)
        signal_composite = Audio_m #signal1 + signal2 + signal3
        time_domain_title = "NANA"#f"Signal with freqs {freq1}Hz, {freq2}Hz, and {freq3}Hz sampled at 800Hz (length: {total_time_in_secs}s)"
        calc_and_plot_xcorr_dft_with_ground_truth(
            signal_composite, samplerate, time_domain_graph_title=time_domain_title)
        plt.show()

    def fourier_analysis(self):
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='disabled')

        fourier_thread = threading.Thread(target=self.run_analysis)
        fourier_thread.start()

        self.btn_start.config(state='normal')
        self.btn_stop.config(state='normal')

    def start_execution(self):
        self.recording = True
        self.btn_start.config(state='disabled')

        audio = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 16000
        CHUNK = 1024
        archivo = "grabacion.wav"
        rec_sound_thread = threading.Thread(
            target=self.record_sound,
            args=(FORMAT, CHANNELS, RATE, CHUNK, audio, archivo)
        )
        count_time_thread = threading.Thread(target=self.chronometer)
        rec_sound_thread.start()
        count_time_thread.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.btn_start.config(state='normal')
            self.time.after_cancel(self.process_timer)
            self.time['text'] = "00"
            self.seconds_counter = 0
        self.read_audio_files()

    def read_audio_files(self):
        lines = self.list_udio_files.size()
        self.list_udio_files.delete(0, lines)
        recordings = glob.glob('*.wav')
        for i, value in enumerate(recordings):
            self.list_udio_files.insert(i+1, value)

    def record_sound(self, format, channels, rate, frames_per_buffer, audio, archivo):
        stream = audio.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=frames_per_buffer
        )

        frames = []

        print("recording.....")
        self.status_recording['text'] = "recording....."
        while self.recording == True:
            data = stream.read(frames_per_buffer)
            frames.append(data)
        self.status_recording['text'] = ".....recording finished"
        print(".....recording finished")

        # DETENEMOS GRABACIÓN
        stream.stop_stream()
        stream.close()
        audio.terminate()

        recordings = glob.glob('*.wav')

        # CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
        count = 0
        for i in recordings:
            if "grabacion" in i:
                count += 1
        if count > 0:
            archivo = "grabacion"+"("+str(count)+")"+".wav"

        waveFile = wave.open(archivo, 'wb')
        waveFile.setnchannels(channels)
        waveFile.setsampwidth(audio.get_sample_size(format))
        waveFile.setframerate(rate)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

    def chronometer(self):
        self.time['text'] = str(self.seconds_counter)
        self.seconds_counter += 1
        self.process_timer = self.time.after(1000, self.chronometer)
