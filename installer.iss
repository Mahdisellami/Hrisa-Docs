[Setup]
AppName=Hrisa Docs
AppVersion=0.1.0
AppPublisher=Hrisa Docs
DefaultDirName={autopf}\HrisaDocs
DefaultGroupName=Hrisa Docs
OutputBaseFilename=HrisaDocs-0.1.0-Setup
Compression=lzma2
SolidCompression=yes
OutputDir=dist
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "installdeps"; Description: "Install required dependencies (Ollama, Pandoc)"; GroupDescription: "Dependencies"; Flags: checkedonce

[Files]
Source: "dist\HrisaDocs.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "scripts\check_dependencies.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Hrisa Docs"; Filename: "{app}\HrisaDocs.exe"
Name: "{autodesktop}\Hrisa Docs"; Filename: "{app}\HrisaDocs.exe"; Tasks: desktopicon

[Run]
Filename: "python"; Parameters: "{app}\check_dependencies.py --auto"; StatusMsg: "Installing dependencies (Ollama, Pandoc)..."; Tasks: installdeps; Flags: waituntilterminated
Filename: "notepad"; Parameters: "{%TEMP}\hrisa_deps_install.log"; Description: "View dependency installation log"; Flags: postinstall skipifsilent nowait unchecked
Filename: "{app}\HrisaDocs.exe"; Description: "{cm:LaunchProgram,Hrisa Docs}"; Flags: nowait postinstall skipifsilent
