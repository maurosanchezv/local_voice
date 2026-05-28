import json
import os
import sys
import pyaudio
import pyperclip  # type: ignore
import keyboard
import customtkinter as ctk  # type: ignore
from vosk import Model, KaldiRecognizer  # type: ignore
import threading
import re
import array

# Lógica de rutas para encontrar archivos ya sea en script o en .exe
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Directorio del ejecutable
        exe_dir = os.path.dirname(sys.executable)
        # Directorio interno (PyInstaller 6+)
        internal_dir = os.path.join(exe_dir, "_internal")
        
        # Verificar si los modelos están en _internal
        if os.path.exists(os.path.join(internal_dir, "vosk-model-small-es-0.42")):
            return internal_dir
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = os.path.abspath(get_base_path())

# Guardar la configuración en AppData para no necesitar permisos de administrador
USER_DATA_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "TranscriptorVozLocal")
if not os.path.exists(USER_DATA_PATH):
    os.makedirs(USER_DATA_PATH)

CONFIG_FILE = os.path.join(USER_DATA_PATH, "config.json")

# Variables globales
transcription_active = False
voice_control_active = False
is_new_sentence = True
last_partial_length = 0

# Caché de modelos para evitar recargas lentas
loaded_models = {}

# Paleta de colores
ACCENT_COLOR = ["#3B8ED0", "#1F6AA5"]
REC_COLOR = "#c0392b"
REC_HOVER = "#e74c3c"
REC_GLOW = "#ff6b5b"
OK_COLOR = "#2ecc71"
ERR_COLOR = "#e74c3c"
IDLE_COLOR = "#dcdcdc"

_pulse_on = False


def set_status(text, color=IDLE_COLOR):
    status_label.configure(text=text, text_color=color)


def update_level_meter(data):
    # Calcula el RMS del audio y lo refleja en la barra de nivel.
    try:
        samples = array.array("h", data)
        if not samples:
            return
        rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
        level_meter.set(min(rms / 3000.0, 1.0))
    except Exception:
        pass


def animate_recording():
    global _pulse_on
    if not transcription_active:
        start_button.configure(border_width=0)
        return
    _pulse_on = not _pulse_on
    start_button.configure(
        border_width=3 if _pulse_on else 0, border_color=REC_GLOW
    )
    root.after(450, animate_recording)


def apply_formatting(text, language):
    global is_new_sentence

    # Reemplazos de puntuación
    if language == "es":
        replacements = {
            r"\bpunto\b": ".",
            r"\bcoma\b": ",",
            r"\bdos puntos\b": ":",
            r"\bpunto y coma\b": ";",
            r"\bsigno de interrogación\b": "?",
            r"\bsigno de exclamación\b": "!",
            r"\bnueva línea\b": "\n",
        }
    elif language == "pt":
        replacements = {
            r"\bponto\b": ".",
            r"\bvírgula\b": ",",
            r"\bdois pontos\b": ":",
            r"\bponto e vírgula\b": ";",
            r"\bponto de interrogação\b": "?",
            r"\bsinal de interrogação\b": "?",
            r"\bponto de exclamação\b": "!",
            r"\bsinal de exclamação\b": "!",
            r"\bnova linha\b": "\n",
        }
    else:  # English
        replacements = {
            r"\bperiod\b": ".",
            r"\bfull stop\b": ".",
            r"\bcomma\b": ",",
            r"\bquestion mark\b": "?",
            r"\bexclamation point\b": "!",
            r"\bnew line\b": "\n",
        }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Lógica de capitalización
    if text:
        if is_new_sentence:
            text = text[0].upper() + text[1:]
            is_new_sentence = False

        # Si termina en signo de puntuación final, la próxima será mayúscula
        if any(text.rstrip().endswith(p) for p in [".", "?", "!", "\n"]):
            is_new_sentence = True

    return text


def change_language(lang_name):
    language_var.set(lang_name)
    if transcription_active:
        # Reiniciar la transcripción para cargar el nuevo modelo
        toggle_transcription() # Detener
        root.after(500, toggle_transcription) # Iniciar tras breve pausa

def process_voice_command(text):
    # Diccionario de comandos con variaciones para mayor robustez
    commands = {
        r"(detener|parar|finalizar) transcripción": toggle_transcription,
        r"(iniciar|empezar) transcripción": toggle_transcription,
        r"copiar texto": copy_text,
        r"limpiar texto": clear_text,
        r"cambiar a español": lambda: change_language("Español"),
        r"cambiar a inglés": lambda: change_language("English"),
        r"cambiar a portugués": lambda: change_language("Português"),
    }
    
    for pattern, action in commands.items():
        if re.search(pattern, text, re.IGNORECASE):
            action()
            # Feedback visual en la etiqueta de estado
            set_status(f"Comando: {text.upper()}", "#5dade2")
            root.after(2000, lambda: set_status("Escuchando...", OK_COLOR))
            return True
    return False


def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            name = device_info["name"]
            try:
                # Corregir codificación para Windows
                name = name.encode('cp1252').decode('utf-8')
            except:
                pass
            devices.append((device_info["index"], name))
    p.terminate()
    return devices


def save_config():
    global device_combobox, config
    try:
        # Intentar obtener el dispositivo del combobox de la UI si existe
        selected_device = device_combobox.get()
    except Exception:
        # Si la ventana está cerrada, intentar usar lo que ya estaba cargado
        selected_device = config.get("device", "")

    data = {
        "device": selected_device,
        "language": language_var.get(),
        "voice_control": voice_control_var.get(),
        "continuous_text": continuous_text_var.get(),
        "opacity": opacity_var.get(),
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
    
    # Actualizar la variable global 'config' para que los cambios surtan efecto sin reiniciar
    config = data


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def transcribe_audio(device_index):
    global transcription_active, voice_control_active, loaded_models
    transcription_active = True
    
    lang_map = {
        "Español": "es",
        "English": "en",
        "Português": "pt"
    }
    language = lang_map.get(language_var.get(), "es")
    
    if language == "es":
        model_path = os.path.join(BASE_PATH, "vosk-model-small-es-0.42")
    elif language == "pt":
        model_path = os.path.join(BASE_PATH, "vosk-model-small-pt-0.3")
    else:
        model_path = os.path.join(BASE_PATH, f"vosk-model-small-{language}")

    if not os.path.exists(model_path):
        set_status(f"Error: Modelo '{model_path}' no encontrado", ERR_COLOR)
        return

    # Usar modelo de la caché si ya está cargado
    if model_path in loaded_models:
        model = loaded_models[model_path]
        set_status("Iniciando rápidamente...")
    else:
        set_status("Iniciando transcriptor...")
        root.update_idletasks()
        try:
            model = Model(model_path)
            loaded_models[model_path] = model  # Guardar en caché
        except Exception as e:
            set_status(f"Error al cargar modelo: {str(e)}", ERR_COLOR)
            return

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

    set_status("Escuchando... Habla ahora", OK_COLOR)

    def process_audio():
        if transcription_active:
            data = stream.read(1000, exception_on_overflow=False)
            if len(data) == 0:
                return
            update_level_meter(data)
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
            set_status("Listo")
            start_button.configure(text="🎙", fg_color=ACCENT_COLOR, border_width=0)
            level_meter.set(0)

    def process_result(result, is_partial=False):
        # Usamos el texto detectado (ya sea parcial o final)
        text = result.get("text", result.get("partial", ""))
        if text:
            # Procesar comandos de voz ANTES que cualquier otra cosa
            if voice_control_active and not is_partial:
                if process_voice_command(text):
                    return

            # Si no es un comando y es un resultado final, escribirlo
            if not is_partial:
                lang_map = {
                    "Español": "es",
                    "English": "en",
                    "Português": "pt"
                }
                language = lang_map.get(language_var.get(), "es")
                formatted_text = apply_formatting(text, language)
                separator = " " if continuous_text_var.get() else "\n"
                keyboard.write(formatted_text + separator)
                print(f"Transcrito: {formatted_text}")

    root.after(10, process_audio)


def toggle_transcription():
    global transcription_active

    if not transcription_active:
        selected_device = device_combobox.get()
        try:
            device_index = next(index for index, name in devices if name == selected_device)  # noqa E501
            save_config()
            transcription_active = True
            start_button.configure(text="🛑", fg_color=REC_COLOR, hover_color=REC_HOVER)
            animate_recording()
            threading.Thread(
                target=transcribe_audio, args=(device_index,), daemon=True
            ).start()
        except StopIteration:
            transcription_active = False
            set_status("Error: Micrófono no encontrado", ERR_COLOR)
    else:
        transcription_active = False
        start_button.configure(text="🎙️", fg_color=ACCENT_COLOR, hover_color=["#367E96", "#144E73"], border_width=0)
        level_meter.set(0)


# Variables globales para rastrear ventanas secundarias
settings_window = None
help_window = None


def toggle_voice_control():
    global voice_control_active
    voice_control_active = voice_control_var.get()
    status = "activado" if voice_control_active else "desactivado"
    set_status(f"Voz {status}")


def open_settings_window():
    global settings_window
    
    if settings_window is not None and settings_window.winfo_exists():
        settings_window.destroy()
        settings_window = None
        return

    settings_window = ctk.CTkToplevel(root)
    settings_window.title("Configuración")
    settings_window.geometry("350x420")
    
    x = root.winfo_x() - 25
    y = root.winfo_y() + 160
    settings_window.geometry(f"+{x}+{y}")
    
    settings_window.attributes("-topmost", True)
    settings_window.resizable(False, False)

    ctk.CTkLabel(settings_window, text="⚙️ Configuración", font=("Arial", 20, "bold")).pack(pady=(25, 15))
    
    # Micrófono
    ctk.CTkLabel(settings_window, text="Micrófono:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
    global device_combobox
    device_combobox = ctk.CTkOptionMenu(
        settings_window, values=[name for _, name in devices], width=280,
        fg_color="#34495e", button_color="#2c3e50"
    )
    device_combobox.pack(pady=5)
    device_combobox.set(config.get("device", devices[0][1] if devices else ""))

    # Idioma
    ctk.CTkLabel(settings_window, text="Idioma de dictado:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
    global language_menu
    language_menu = ctk.CTkOptionMenu(
        settings_window, variable=language_var, values=["Español", "English", "Português"], 
        width=280, fg_color="#34495e", button_color="#2c3e50"
    )
    language_menu.pack(pady=5)

    # Opciones
    ctk.CTkCheckBox(
        settings_window, text="Texto continuo (Espacio en lugar de Enter)", 
        variable=continuous_text_var, font=("Arial", 11)
    ).pack(pady=(15, 5), padx=35, anchor="w")
    
    # Transparencia
    ctk.CTkLabel(settings_window, text="Transparencia de ventana:", font=("Arial", 12, "bold")).pack(pady=(15, 0))
    def on_opacity_change(value):
        root.attributes("-alpha", float(value))
    
    ctk.CTkSlider(
        settings_window, from_=0.4, to=1.0, variable=opacity_var,
        command=on_opacity_change, width=280
    ).pack(pady=5)

    def close_settings():
        save_config()
        settings_window.destroy()

    ctk.CTkButton(
        settings_window, text="Guardar y Cerrar", command=close_settings,
        fg_color=ACCENT_COLOR, hover_color="#2980b9", width=200, height=35
    ).pack(pady=(25, 20))


def show_help():
    global help_window
    
    if help_window is not None and help_window.winfo_exists():
        help_window.destroy()
        help_window = None
        return

    help_window = ctk.CTkToplevel(root)
    help_window.title("Ayuda")
    help_window.geometry("350x450")
    
    x = root.winfo_x() - 25
    y = root.winfo_y() + 160
    help_window.geometry(f"+{x}+{y}")
    
    help_window.attributes("-topmost", True)
    help_window.resizable(False, False)

    ctk.CTkLabel(help_window, text="❓ Guía de Uso", font=("Arial", 20, "bold")).pack(pady=(25, 15))

    text = (
        "1. Activar Micrófono:\n"
        "   - Clic en el botón (🎙) o tecla F9.\n"
        "   - El botón pulsará en rojo al grabar.\n\n"
        "2. Dictado Automático:\n"
        "   - El programa escribe donde esté tu cursor.\n"
        "   - Gestiona mayúsculas automáticamente.\n\n"
        "3. Puntuación por voz:\n"
        "   - Di 'punto', 'coma' o 'nueva línea'.\n\n"
        "4. Nivel de Audio:\n"
        "   - La barra inferior muestra la intensidad.\n\n"
        "5. Configuración (⚙️):\n"
        "   - Cambia el idioma y la transparencia."
    )
    
    # Frame para el texto con un poco de color de fondo sutil
    info_frame = ctk.CTkFrame(help_window, fg_color="#2c3e50", corner_radius=10)
    info_frame.pack(pady=10, padx=20, fill="both", expand=True)

    ctk.CTkLabel(
        info_frame, text=text, justify="left", font=("Arial", 12), 
        wraplength=280, text_color="#ecf0f1"
    ).pack(pady=15, padx=15)
    
    ctk.CTkButton(
        help_window, text="Entendido", command=help_window.destroy,
        fg_color=ACCENT_COLOR, hover_color="#2980b9", width=200, height=35
    ).pack(pady=(15, 20))


# Limpieza de funciones obsoletas
def clear_text():
    """Limpia el texto (placeholder para futuras expansiones)"""
    pass

def copy_text():
    """Copia el texto al portapapeles (placeholder para futuras expansiones)"""
    pass

# Registrar hotkey global para accesibilidad (F9 para alternar micrófono)
try:
    keyboard.add_hotkey('f9', toggle_transcription)
except Exception as e:
    print(f"No se pudo registrar el hotkey: {e}")

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear la ventana principal (Modo Widget Ultra Compacto)
root = ctk.CTk()
root.title("Voz")
root.geometry("300x150")  # Espacio para el estado y el medidor de nivel
root.attributes("-topmost", True)
root.resizable(False, False)

# Variables de control
config = load_config()
devices = get_audio_devices()
language_var = ctk.StringVar(value=config.get("language", "Español"))
voice_control_var = ctk.BooleanVar(value=config.get("voice_control", True))
continuous_text_var = ctk.BooleanVar(value=config.get("continuous_text", True))
opacity_var = ctk.DoubleVar(value=config.get("opacity", 0.92))
voice_control_active = voice_control_var.get()
root.attributes("-alpha", opacity_var.get())

# Frame central (Centrado absoluto)
button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.place(relx=0.5, rely=0.5, anchor="center")

# Botón de Configuración (Círculo Pequeño)
settings_button = ctk.CTkButton(
    button_frame, text="⚙️", width=44, height=44, font=("Arial", 20),
    command=open_settings_window, fg_color="transparent", hover_color="gray30",
    corner_radius=22, border_width=0
)
settings_button.pack(side="left", padx=5)

# Botón de Micrófono (Círculo Grande)
start_button = ctk.CTkButton(
    button_frame, text="🎙", width=64, height=64, font=("Arial", 28),
    command=toggle_transcription, anchor="center", corner_radius=32
)
start_button.pack(side="left", padx=10)

# Botón de Ayuda (Círculo Pequeño)
help_button = ctk.CTkButton(
    button_frame, text="❓", width=44, height=44, font=("Arial", 20),
    command=show_help, fg_color="transparent", hover_color="gray30",
    corner_radius=22, border_width=0
)
help_button.pack(side="left", padx=5)


# Dummy invisible para lógica
device_combobox = ctk.CTkOptionMenu(root)
device_combobox.set(config.get("device", devices[0][1] if devices else ""))

# Etiqueta de estado visible (Importante para accesibilidad)
status_label = ctk.CTkLabel(root, text="Presiona F9 para grabar", font=("Arial", 12))
status_label.pack(pady=(0, 5))

# Medidor de nivel de micrófono
level_meter = ctk.CTkProgressBar(root, height=6, corner_radius=3)
level_meter.set(0)
level_meter.pack(side="bottom", fill="x", padx=25, pady=(0, 10))

root.mainloop()
