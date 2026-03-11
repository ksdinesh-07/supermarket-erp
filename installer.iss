[Setup]
AppName=Supermarket ERP
AppVersion=1.0
AppPublisher=KSDinesh-07
AppPublisherURL=https://github.com/ksdinesh-07/supermarket-erp
AppSupportURL=https://github.com/ksdinesh-07/supermarket-erp/issues
DefaultDirName={autopf}\SupermarketERP
DefaultGroupName=Supermarket ERP
UninstallDisplayIcon={app}\SupermarketERP.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=SupermarketERP_Setup
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Files]
Source: "dist\SupermarketERP.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "database\*.py"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "database\*.sql"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "modules\*.py"; DestDir: "{app}\modules"; Flags: ignoreversion
Source: "modules\*\*.py"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs
Source: "ui\styles\*.qss"; DestDir: "{app}\ui\styles"; Flags: ignoreversion
Source: "utils\*.py"; DestDir: "{app}\utils"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Supermarket ERP"; Filename: "{app}\SupermarketERP.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall Supermarket ERP"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Supermarket ERP"; Filename: "{app}\SupermarketERP.exe"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userstartmenu}\Supermarket ERP"; Filename: "{app}\SupermarketERP.exe"; WorkingDir: "{app}"; Tasks: startmenuicon

[Run]
Filename: "{app}\SupermarketERP.exe"; Description: "Launch Supermarket ERP"; Flags: postinstall nowait skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /f /im SupermarketERP.exe 2>nul"; Flags: runhidden

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('This will install Supermarket ERP on your computer.' + #13#13 +
         'Default login: admin / admin123' + #13#13 +
         'Click OK to continue.', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if MsgBox('Installation complete! Start Supermarket ERP now?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(ExpandConstant('{app}\SupermarketERP.exe'), '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
end;
