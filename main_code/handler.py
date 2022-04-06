import glob
import pyaudio
import wave
from tkinter import Button, Frame, Label, Tk, Listbox
import threading


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
        self.btn_iniciar = Button(frame2, fg='blue', width=16,
                                  text='Grabar', command=self.start_execution)
        self.btn_iniciar.grid(row=0, column=0)

        self.btn_parar = Button(frame2, fg='blue', width=16,
                                text='Parar', command=self.stop_recording)
        self.btn_parar.grid(row=0, column=1)

        # listbox
        self.list_udio_files = Listbox(frame3)
        self.list_udio_files.pack()

    def start_execution(self):
        self.recording = True
        self.btn_iniciar.config(state='disabled')

        audio = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        CHUNK = 1024
        archivo = "grabacion.mp3"
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
            self.btn_iniciar.config(state='normal')
            self.time.after_cancel(self.process_timer)
            self.time['text'] = "00"
            self.seconds_counter = 0
        self.read_audio_files()

    def read_audio_files(self):
        lines = self.list_udio_files.size()
        self.list_udio_files.delete(0, lines)
        recordings = glob.glob('*.mp3')
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

        recordings = glob.glob('*.mp3')

        # CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
        count = 0
        for i in recordings:
            if "grabacion" in i:
                count += 1
        if count > 0:
            archivo = "grabacion"+"("+str(count)+")"+".mp3"

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
