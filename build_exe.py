import PyInstaller.__main__
import os
import shutil
import vosk
import customtkinter
import time

# Nombre del archivo principal
main_script = "reconocimiento.py"

# Limpieza previa con reintentos para evitar errores de permisos
folders_to_clean = ["build", "dist"]
for folder in folders_to_clean:
    if os.path.exists(folder):
        print(f"Limpiando carpeta: {folder}...")
        try:
            shutil.rmtree(folder)
        except PermissionError:
            print(f"⚠️ ERROR: No se pudo limpiar {folder}. El programa o un archivo están en uso.")
            print("Esperando 3 segundos para reintentar... (Cierra el programa si está abierto)")
            time.sleep(3)
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"❌ Error crítico: {e}")
                print("No se puede continuar. Por favor, cierra TranscriptorVozLocal.exe y reintenta.")
                exit(1)

# Obtener rutas de las librerías
vosk_path = os.path.dirname(vosk.__file__)
ctk_path = os.path.dirname(customtkinter.__file__)

# Nombres exactos de los modelos
modelos = [
    "vosk-model-small-es-0.42",
    "vosk-model-small-en",
    "vosk-model-small-pt-0.3"
]

# Configuración de PyInstaller
params = [
    main_script,
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name=TranscriptorVozLocal",
    "--clean",
    # Añadir librerías necesarias explícitamente
    f"--add-data={vosk_path};vosk/",
    f"--add-data={ctk_path};customtkinter/",
]

# Añadir modelos a la configuración de PyInstaller
for modelo in modelos:
    if os.path.exists(modelo):
        params.append(f"--add-data={modelo};{modelo}/")
    else:
        print(f"⚠️ Advertencia: El modelo {modelo} no se encontró en la raíz y no se incluirá.")

print(f"Ruta de Vosk encontrada: {vosk_path}")
print(f"Ruta de CustomTkinter encontrada: {ctk_path}")
print("Iniciando proceso de creación del ejecutable...")

try:
    PyInstaller.__main__.run(params)
    print("\n¡Compilación de PyInstaller finalizada con éxito!")
    
    # Verificación extra: Asegurarse de que los modelos estén en _internal
    # PyInstaller a veces los pone en la raíz del dist o en _internal según la versión
    dest_path = os.path.join("dist", "TranscriptorVozLocal", "_internal")
    
    if os.path.exists(dest_path):
        print(f"Verificando modelos en {dest_path}...")
        for modelo in modelos:
            mod_dest = os.path.join(dest_path, modelo)
            if not os.path.exists(mod_dest) and os.path.exists(modelo):
                print(f"Copiando {modelo} manualmente a _internal para asegurar detección...")
                shutil.copytree(modelo, mod_dest)
    
    print("\n¡Proceso de construcción completo! Ahora puedes usar Inno Setup.")

except Exception as e:
    print(f"❌ Error durante la creación del ejecutable: {e}")
