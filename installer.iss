#define MyAppName "疯狂俄罗斯方块"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "疯狂俄罗斯方块.exe"

[Setup]
AppId={{A45C7511-3E6F-4A47-A8A1-4C52C4EF4D21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename={#MyAppName}_Setup
SetupIconFile=assets\textures\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Shortcut"; GroupDescription: "Additional Tasks:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch application after installation"; Flags: nowait postinstall skipifsilent
