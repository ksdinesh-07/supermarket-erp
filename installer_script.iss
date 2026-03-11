[Setup]
AppName=Supermarket ERP
AppVersion=1.0
AppPublisher=Your Company
AppPublisherURL=https://yourwebsite.com
DefaultDirName={pf}\SupermarketERP
DefaultGroupName=Supermarket ERP
UninstallDisplayIcon={app}\SupermarketERP.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=SupermarketERP_Setup
SetupIconFile=app_icon.ico
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "mysql"; Description: "Install MySQL Database (Recommended)"; GroupDescription: "Database setup:"; Flags: checkedonce

[Files]
Source: "dist\SupermarketERP.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "database\schema.sql"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "database\schema_update_fixed.sql"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "mysql-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Tasks: mysql

[Icons]
Name: "{group}\Supermarket ERP"; Filename: "{app}\SupermarketERP.exe"
Name: "{group}\Uninstall Supermarket ERP"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Supermarket ERP"; Filename: "{app}\SupermarketERP.exe"; Tasks: desktopicon

[Run]
Filename: "{tmp}\mysql-installer.exe"; Description: "Install MySQL"; Flags: runascurrentuser skipifsilent; Tasks: mysql
Filename: "{app}\SupermarketERP.exe"; Description: "Launch Supermarket ERP"; Flags: postinstall nowait skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create database automatically
    Exec('mysql', '-u root -p -e "CREATE DATABASE IF NOT EXISTS supermarket_erp"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('mysql', '-u root -p supermarket_erp < "{app}\database\schema.sql"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
