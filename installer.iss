; Inno Setup script for Invoice Genius
; Created by DevDuo Gemini Agent

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{F2A5F0A8-7241-4A5C-A7A8-6389A8A97B4E}}
AppName=Invoice Genius
AppVersion=1.0.0
AppPublisher=DevDuo Innovation
DefaultDirName={autopf}\Invoice Genius
DefaultGroupName=Invoice Genius
DisableProgramGroupPage=yes
; OutputDir=installer will create a subfolder for the setup file
OutputDir=installer
OutputBaseFilename=InvoiceGenius-Setup-v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; NOTE: "Source" should point to the folder where your built application (Invoice Genius.exe and its dependencies) is located.
; This script assumes it is in a 'dist' subfolder relative to the script.
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Invoice Genius"; Filename: "{app}\Invoice Genius.exe"
Name: "{autodesktop}\Invoice Genius"; Filename: "{app}\Invoice Genius.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Invoice Genius.exe"; Description: "{cm:LaunchProgram,Invoice Genius}"; Flags: nowait postinstall skipifsilent
