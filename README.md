# 🎙️ Transcriptor de Voz Local (Modo Widget)

Un transcriptor de voz a texto de alta fidelidad, **totalmente local y privado**, diseñado específicamente para la **accesibilidad en videojuegos y productividad**. Ideal para usuarios que necesitan dictar texto sin utilizar el teclado.

---

## 🚀 Instalación Rápida (Recomendado)

Para usuarios que solo quieren usar el programa en Windows sin instalar Python:

1. Ve a la sección de **[Releases](https://github.com/maurosanchezv/local_voice/releases)**.
2. Descarga el archivo más reciente: `Instalador_Transcriptor_Voz_v1.1.exe`.
3. Ejecuta el instalador y sigue las instrucciones.
4. **Nota importante:** Al ser un desarrollador independiente, Windows mostrará un aviso de *"SmartScreen"*. Para continuar, haz clic en **"Más información"** y luego en **"Ejecutar de todas formas"**. El programa es 100% seguro y de código abierto.

---

## ✨ Características Principales
- **Interfaz Minimalista**: Barra flotante ultra compacta que se mantiene siempre al frente (Always on Top).
- **Escritura Directa**: El programa escribe automáticamente en la ventana que tengas activa (juego, chat, Word, etc.).
- **Multilingüe**: Soporte integrado para **Español, Inglés y Portugués**.
- **100% Local**: No requiere internet. Tus datos y voz nunca salen de tu ordenador.
- **Puntuación por Voz**: Dicta "punto", "coma" o "nueva línea" de forma natural.
- **Hotkeys**: Pulsa **F9** para activar/desactivar el dictado rápidamente desde cualquier lugar.

## 🛠️ Uso y Configuración
1. Abre el programa desde el acceso directo del escritorio.
2. Haz clic en el icono de **Engranaje (⚙️)** para configurar tu micrófono y el idioma.
3. Haz clic en el **Micrófono (🎙️)** para empezar a dictar. El icono cambiará a un Stop (🛑) rojo mientras esté escuchando.
4. Puedes usar **Comandos de Voz** como *"detener transcripción"* o *"cambiar a inglés"*.

---

## 💻 Desarrollo y Compilación Manual
Si eres desarrollador y quieres modificar el código:

1. **Requisitos**: Python 3.10+
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Modelos de Voz**: Descarga los modelos de Vosk y colócalos en la raíz:
   - `vosk-model-small-es-0.42`
   - `vosk-model-small-en`
   - `vosk-model-small-pt-0.3`
4. **Ejecutar**: `python reconocimiento.py`
5. **Compilar a EXE**: 
   ```bash
   python build_exe.py
   ```

---
Desarrollado con enfoque en la accesibilidad. 100% Privado.
