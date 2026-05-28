; Script de Inno Setup actualizado para Transcriptor de Voz Local
#define MyAppName "Transcriptor de Voz Local"
#define MyAppVersion "1.1"
#define MyAppPublisher "Mauro Sanchez"
#define MyAppExeName "TranscriptorVozLocal.exe"

[Setup]
; NOTA: El AppId identifica de forma única esta aplicación. No uses el mismo para otras apps.
AppId={{8B3C4A12-5F6D-4E7B-9A1C-D2E3F4G5H6I7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Permitir que el usuario elija la carpeta (recomendado)
DisableDirPage=no
; Icono que aparecerá en el panel de control
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
OutputDir=dist\Installer
OutputBaseFilename=Instalador_Transcriptor_Voz_v1.1
PrivilegesRequired=admin
; Optimización para Windows moderno
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia todo el contenido generado por PyInstaller (incluyendo la carpeta _internal y modelos)
Source: "dist\TranscriptorVozLocal\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Opcional: Si quieres incluir el archivo LEEME en la carpeta de instalación
Source: "LEEME.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Opción de ejecutar la aplicación al terminar la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpiar archivos temporales o de configuración si fuera necesario
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\vosk-model-*"
