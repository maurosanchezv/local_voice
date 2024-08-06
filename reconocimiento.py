import json
import os
import pyaudio
import pyperclip  # type: ignore
import keyboard
import customtkinter as ctk  # type: ignore
from vosk import Model, KaldiRecognizer  # type: ignore
import threading
import re


CONFIG_FILE = "config.json"

# Variables globales
transcription_active = False
voice_control_active = False


def process_voice_command(text):
    commands = {
        r"iniciar transcripción": toggle_transcription,
        r"detener transcripción": toggle_transcription,
        r"copiar texto": copy_text,
        r"limpiar texto": clear_text,
        r"cambiar a español": lambda: language_var.set("Español"),
        r"cambiar a inglés": lambda: language_var.set("English"),
    }
    for command, action in commands.items():
        if re.search(command, text, re.IGNORECASE):
            action()
            return True
    return False


def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            devices.append((device_info["index"], device_info["name"]))
    p.terminate()
    return devices


def save_config(device, language):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"device": device, "language": language}, f)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def transcribe_audio(device_index):
    global transcription_active, voice_control_active
    transcription_active = True
    language = "es" if language_var.get() == "Español" else "en"
    model_path = f"vosk-model-small-{language}"

    if not os.path.exists(model_path):
        status_label.configure(
            text=f"Error: Modelo de lenguaje '{language}' no encontrado"
        )
        return

    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=2000,
    )
    stream.start_stream()

    status_label.configure(text="Escuchando... Habla ahora")

    def process_audio():
        if transcription_active:
            data = stream.read(1000, exception_on_overflow=False)
            if len(data) == 0:
                return
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                process_result(result)
            else:
                partial = json.loads(rec.PartialResult())
                process_result(partial, is_partial=True)

            root.after(10, process_audio)
        else:
            stream.stop_stream()
            stream.close()
            p.terminate()
            status_label.configure(text="Listo para transcribir")
            start_button.configure(text="Iniciar Transcripción")

    def process_result(result, is_partial=False):
        if result.get("text", ""):
            text = result["text"]
            if voice_control_active and process_voice_command(text):
                return
            if write_anywhere_var.get():
                if not is_partial:
                    keyboard.write(text + " ")
            else:
                if is_partial:
                    text_output.delete("end-1l", "end")
                text_output.insert("end", text + "\n")
                text_output.see("end")
            print(f"Transcrito: {text}")  # Imprimir en consola

    root.after(10, process_audio)


def toggle_transcription():
    global transcription_active

    if not transcription_active:
        start_button.configure(text="Detener Transcripción")
        selected_device = device_combobox.get()
        device_index = next(index for index, name in devices if name == selected_device)  # noqa E501
        save_config(selected_device, language_var.get())
        threading.Thread(
            target=transcribe_audio, args=(device_index,), daemon=True
        ).start()
    else:
        transcription_active = False


def toggle_voice_control():
    global voice_control_active
    voice_control_active = voice_control_var.get()
    status_label.configure(
        text=f"Control por voz {
            'activado' if voice_control_active else 'desactivado',
            }"
    )


# Añade esta función para limpiar el texto
def clear_text():
    text_output.delete("1.0", "end")
    status_label.configure(text="Texto limpiado")


def start_transcription():
    selected_device = device_combobox.get()
    device_index = next(
        index for index, name in devices if name == selected_device
    )  # noqa E501
    save_config(selected_device, language_var.get())
    transcribe_audio(device_index)


def copy_text():
    text = text_output.get("0.0", "end")
    pyperclip.copy(text)
    status_label.configure(text="Texto copiado al portapapeles")


# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear la ventana principal
root = ctk.CTk()
root.title("Transcriptor de Voz Local")
root.geometry("500x600")
root.attributes("-topmost", True)

# Frame principal
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Obtener dispositivos de audio
devices = get_audio_devices()

# Cargar configuración
config = load_config()

# Widgets
device_label = ctk.CTkLabel(main_frame, text="Selecciona el micrófono:")
device_label.pack(pady=10)

device_combobox = ctk.CTkOptionMenu(
    main_frame, values=[name for _, name in devices], width=300
)
device_combobox.pack(pady=5)
device_combobox.set(
    config.get(
        "device", devices[0][1] if devices else "No se encontraron micrófonos"
    )  # noqa E501
)

# En la sección de widgets, añade:
voice_control_var = ctk.BooleanVar()
voice_control_check = ctk.CTkCheckBox(
    main_frame,
    text="Control por voz",
    variable=voice_control_var,
    command=toggle_voice_control,
)
voice_control_check.pack(pady=5)

# Selector de idioma
language_var = ctk.StringVar(value=config.get("language", "Español"))
language_label = ctk.CTkLabel(main_frame, text="Selecciona el idioma:")
language_label.pack(pady=5)
language_menu = ctk.CTkOptionMenu(
    main_frame, variable=language_var, values=["Español", "English"], width=300
)
language_menu.pack(pady=5)

start_button = ctk.CTkButton(
    main_frame, text="Iniciar Transcripción", command=toggle_transcription
)
start_button.pack(pady=10)

write_anywhere_var = ctk.BooleanVar()
write_anywhere_check = ctk.CTkCheckBox(
    main_frame, text="Escribir en cualquier lugar", variable=write_anywhere_var
)
write_anywhere_check.pack(pady=5)

status_label = ctk.CTkLabel(main_frame, text="Listo para transcribir")
status_label.pack(pady=5)

text_output = ctk.CTkTextbox(main_frame, height=200, width=400)
text_output.pack(pady=10, fill="both", expand=True)

copy_button = ctk.CTkButton(main_frame, text="Copiar Texto", command=copy_text)
copy_button.pack(pady=5)

root.mainloop()
