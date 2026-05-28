# 🎙️ Transcriptor de Voz Local (Modo Widget)

Un transcriptor de voz a texto de alta fidelidad, totalmente local y diseñado específicamente para la **accesibilidad en videojuegos y productividad**. Ideal para usuarios que necesitan dictar texto sin utilizar el teclado, funcionando de forma fluida y privada.

## ✨ Características Principales
- **Interfaz Minimalista (Modo Widget)**: Una barra flotante ultra compacta que se mantiene siempre al frente, diseñada para no estorbar durante el gaming.
- **Escritura Directa**: Elimina la necesidad de copiar y pegar. El programa escribe directamente en la ventana activa (juego, chat, documento).
- **Caché Inteligente de Modelos**: Los modelos de voz se cargan en la RAM una sola vez, permitiendo iniciar y detener la transcripción de forma instantánea.
- **Multilingüe**: Soporte optimizado para Español, Inglés y Portugués (Brasil).
- **Puntuación por Voz**: Dicta signos de puntuación de forma natural ("punto", "coma", "nueva línea", etc.).
- **Control Total por Voz**: Comandos para iniciar, detener o cambiar de idioma sin usar el ratón.

## 🛠️ Instalación y Requisitos

1. **Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Modelos de Voz**:
   El programa está configurado para usar modelos ligeros de Vosk. Asegúrate de tener estas carpetas en el directorio raíz:
   - `vosk-model-small-es-0.42` (Español)
   - `vosk-model-small-en` (Inglés)
   - `vosk-model-small-pt-0.3` (Portugués)

## 🚀 Uso del Programa

1. Ejecuta el script: `python reconocimiento.py`.
2. **Configuración (⚙️)**: Pulsa el botón de engranaje para seleccionar tu micrófono e idioma.
3. **Transcripción (🎙️)**: Pulsa el micrófono central para empezar a hablar. El icono cambiará a un Stop (🛑) rojo mientras escuche.
4. **Ayuda (❓)**: Consulta la lista de comandos de voz y signos de puntuación integrados.

## 📦 Compilación a Ejecutable (.exe)

Si deseas usarlo como una aplicación independiente de Windows:
1. Ejecuta el script de construcción:
   ```bash
   python build_exe.py
   ```
2. Ve a la carpeta `dist/TranscriptorVozLocal/`.
3. **Importante**: Copia tus carpetas de modelos dentro de esa misma carpeta.
4. Ejecuta `TranscriptorVozLocal.exe`.

## 🎤 Comandos de Voz Incluidos
- **Acciones**: "iniciar transcripción", "detener transcripción", "cambiar a español", "cambiar a inglés".
- **Puntuación**: "punto", "coma", "dos puntos", "signo de interrogación", "nueva línea".

---
Desarrollado con enfoque en la accesibilidad para personas con movilidad reducida. 100% Privado y Local.
