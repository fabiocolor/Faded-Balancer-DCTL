; Faded Balancer DCTL - Inno Setup script
; Build from repo root: iscc installers/win/FadedBalancerDCTL.iss
; Or from this dir: iscc FadedBalancerDCTL.iss (after copying FadedBalancerDCTL.dctl here or adjusting Source path)
; Requires Inno Setup: https://jrsoftware.org/isinfo.php

#define MyAppName "Faded Balancer DCTL"
#ifndef MyAppVersion
#define MyAppVersion "1.6.0"
#endif
#define MyAppId "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"
#define ResolveLUTPath "Blackmagic Design\DaVinci Resolve\Support\LUT"
#define DctlFile "FadedBalancerDCTL.dctl"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Fabio Color
DefaultDirName={commonappdata}\{#ResolveLUTPath}
DefaultGroupName={#MyAppName}
; Install the single file to Resolve LUT path; no directory prompt
DisableDirPage=yes
DisableProgramGroupPage=yes
; Admin required to write to ProgramData
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=FadedBalancerDCTL-Setup-{#MyAppVersion}
OutputDir=..
Compression=lzma2
SolidCompression=yes
; Single-package: same exe can be run again to uninstall (maintenance dialog)
UninstallDisplayName={#MyAppName}

[Files]
; Source path relative to .iss file: repo root is ..\..
Source: "..\..\FadedBalancerDCTL.dctl"; DestDir: "{commonappdata}\{#ResolveLUTPath}"; DestName: "{#DctlFile}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut to uninstall (so user has a clear uninstall option)
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Code]
function RunUninstall(const UninstallStr: string; const SilentMode: Boolean): Boolean;
var
  ExePath: string;
  Params: string;
  PosSpace: integer;
  ResultCode: integer;
  Cmd: string;
  ShowCmd: Integer;
begin
  Result := False;
  Cmd := Trim(UninstallStr);
  ExePath := '';
  Params := '';

  if (Length(Cmd) >= 2) and (Cmd[1] = '"') then
  begin
    PosSpace := 2;
    while (PosSpace <= Length(Cmd)) and (Cmd[PosSpace] <> '"') do
      PosSpace := PosSpace + 1;
    if PosSpace <= Length(Cmd) then
    begin
      ExePath := Copy(Cmd, 2, PosSpace - 2);
      Params := Trim(Copy(Cmd, PosSpace + 1, MaxInt));
    end;
  end;

  if ExePath = '' then
  begin
    PosSpace := Pos(' ', Cmd);
    if PosSpace > 0 then
    begin
      ExePath := Copy(Cmd, 1, PosSpace - 1);
      Params := Trim(Copy(Cmd, PosSpace + 1, MaxInt));
    end
    else
      ExePath := Cmd;
  end;

  if (ExePath <> '') and FileExists(ExePath) then
  begin
    if SilentMode then
      ShowCmd := SW_HIDE
    else
      ShowCmd := SW_SHOW;

    if Exec(ExePath, Params, '', ShowCmd, ewWaitUntilTerminated, ResultCode) then
      Result := True;
  end;
end;

function InitializeSetup(): Boolean;
var
  UninstallKey: string;
  UninstallStr: string;
  DctlPath: string;
  HasInstaller: Boolean;
  HasFile: Boolean;
  Choice: Integer;
begin
  Result := True;
  UninstallKey := 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' + '{#MyAppId}_is1';
  DctlPath := ExpandConstant('{commonappdata}') + '\Blackmagic Design\DaVinci Resolve\Support\LUT\FadedBalancerDCTL.dctl';

  HasInstaller := RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', UninstallStr) and (UninstallStr <> '');
  HasFile := FileExists(DctlPath);

  if HasInstaller or HasFile then
  begin
    if WizardSilent then
    begin
      if HasInstaller then
        if not RunUninstall(UninstallStr + ' /VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART', True) then;
      if HasFile then
        if DeleteFile(DctlPath) then;
      Result := True;
      Exit;
    end;

    Choice := MsgBox('A previous version of Faded Balancer DCTL is already installed.' #13#10 #13#10
      'Choose an option:' #13#10
      '- Yes: Replace and install' #13#10
      '- No: Uninstall only' #13#10
      '- Cancel: Exit setup', mbConfirmation, MB_YESNOCANCEL);

    if Choice = IDYES then
    begin
      { Replace: remove file if present and continue }
      if HasFile then
        if DeleteFile(DctlPath) then;
      Result := True;
    end
    else if Choice = IDNO then
    begin
      { Uninstall only: use uninstaller if available, else delete file }
      if HasInstaller then
      begin
        if not RunUninstall(UninstallStr, False) then
          MsgBox('Uninstall may have failed. You can also remove it from Settings > Apps.', mbError, MB_OK);
      end
      else if HasFile then
      begin
        if not DeleteFile(DctlPath) then
          MsgBox('Could not remove the file. You may need to run as administrator.', mbError, MB_OK);
      end;
      Result := False;
    end
    else
      Result := False;
  end;
end;
