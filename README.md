# Transcriptor de Voz Local

Este es un programa que transcribe todo lo que se dice a través del micrófono, utilizando Python y varias bibliotecas. Esta versión funciona de forma local, sin necesidad de conexión a Internet.

## Requisitos

Asegúrate de tener instaladas las siguientes bibliotecas de Python:

- `speech_recognition`
- `pyaudio`
- `pyperclip`
- `keyboard`
- `customtkinter`
- `vosk`

Puedes instalar las dependencias con el siguiente comando:

```bash
pip install -r requirements.txt
Uso
Ejecuta el programa.
Selecciona el micrófono y el idioma desde la interfaz.
Haz clic en "Iniciar Transcripción" para comenzar a transcribir.
El texto transcrito se mostrará en el área de texto.
Puedes copiar el texto al portapapeles con el botón "Copiar Texto".
Configuración
El programa guarda la configuración seleccionada (micrófono e idioma) en un archivo config.json

Interfaz de Usuario
La interfaz está construida con customtkinter, con un tema oscuro y moderno.

Notas
Asegúrate de tener conexión a Internet, ya que el reconocimiento de voz utiliza la API de Google.
El programa permite escribir el texto transcrito en cualquier lugar habilitando la opción correspondiente.
```
