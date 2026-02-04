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
function InitializeSetup(): Boolean;
var
  UninstallKey: string;
  UninstallStr: string;
  DctlPath: string;
  PosSpace: integer;
  ExePath: string;
  Params: string;
  ResultCode: integer;
begin
  Result := True;
  UninstallKey := 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' + '{#MyAppId}_is1';
  DctlPath := ExpandConstant('{commonappdata}') + '\Blackmagic Design\DaVinci Resolve\Support\LUT\FadedBalancerDCTL.dctl';

  { Already installed by this installer: offer to run uninstall }
  if RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', UninstallStr) and (UninstallStr <> '') then
  begin
    if MsgBox('Faded Balancer DCTL is already installed.' #13#10 'Do you want to uninstall it?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      { UninstallString is e.g. "C:\path\to\unins000.exe" /u "C:\path" - parse quoted exe path then rest as params }
      UninstallStr := Trim(UninstallStr);
      ExePath := '';
      Params := '';
      if (Length(UninstallStr) >= 2) and (UninstallStr[1] = '"') then
      begin
        PosSpace := 2;
        while (PosSpace <= Length(UninstallStr)) and (UninstallStr[PosSpace] <> '"') do
          PosSpace := PosSpace + 1;
        if PosSpace <= Length(UninstallStr) then
        begin
          ExePath := Copy(UninstallStr, 2, PosSpace - 2);
          Params := Trim(Copy(UninstallStr, PosSpace + 1, MaxInt));
        end;
      end;
      if ExePath = '' then
      begin
        PosSpace := Pos(' ', UninstallStr);
        if PosSpace > 0 then
        begin
          ExePath := Copy(UninstallStr, 1, PosSpace - 1);
          Params := Trim(Copy(UninstallStr, PosSpace + 1, MaxInt));
        end
        else
          ExePath := UninstallStr;
      end;
      if (ExePath <> '') and FileExists(ExePath) then
      begin
        { Wait for uninstall to finish so registry is removed; then next run will offer install }
        if Exec(ExePath, Params, '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
          MsgBox('Uninstall completed. You can now run this setup again to install.', mbInformation, MB_OK)
        else
          MsgBox('Uninstall may have failed. If the message appears again, use Settings > Apps to uninstall.', mbError, MB_OK);
      end
      else
      begin
        { Uninstaller missing (e.g. deleted); remove registry key and DCTL so next run can install }
        if DeleteFile(DctlPath) then;
        RegDeleteKeyIncludingSubkeys(HKLM, UninstallKey);
        MsgBox('Removed leftover entries. Run this setup again to install.', mbInformation, MB_OK);
      end;
      Result := False;
    end;
    Exit;
  end;

  { DCTL present but not from our installer (e.g. manual copy): offer to remove }
  if FileExists(DctlPath) then
  begin
    if MsgBox('Faded Balancer DCTL is already present in the Resolve LUT folder.' #13#10 'Do you want to remove it?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      if DeleteFile(DctlPath) then
        MsgBox('Faded Balancer DCTL was removed.', mbInformation, MB_OK)
      else
        MsgBox('Could not remove the file. You may need to run as administrator.', mbError, MB_OK);
      Result := False;
    end;
    Exit;
  end;

  { Not installed: proceed with install }
end;
