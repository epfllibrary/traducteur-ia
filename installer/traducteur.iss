#define MyAppName "Traducteur"
#define MyAppVersion "1.0"
#define MyAppPublisher "Sylvain Vuilleumier"
#define MyAppURL "https://gitlab.epfl.ch/sisb-public/id/traducteur"
#define MyAppExeName "traducteur.exe"
#define OllamaSetupURL "https://ollama.com/download/OllamaSetup.exe"
#define AppMutexName "TraducteurAppMutex-8E28A203-8A35-4F78-BE6B-FD0718E146AD"
#define SetupMutexName "TraducteurSetupMutex-8E28A203-8A35-4F78-BE6B-FD0718E146AD"
#ifndef MyAppExeSource
#define MyAppExeSource "..\dist\traducteur.exe"
#endif

[Setup]
AppId={{8E28A203-8A35-4F78-BE6B-FD0718E146AD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userpf}\Traducteur
DefaultGroupName=Traducteur
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
AppMutex={#AppMutexName}
SetupMutex={#SetupMutexName}
CloseApplications=yes
RestartApplications=no
OutputDir=..\dist
OutputBaseFilename=traducteur-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
LicenseFile=..\LICENSE
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion=1.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Installateur de Traducteur
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis supplémentaires :"; Flags: unchecked
Name: "startupicon"; Description: "Lancer Traducteur automatiquement à l'ouverture de session"; GroupDescription: "Démarrage automatique :"

[Files]
Source: "{#MyAppExeSource}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
Source: "..\.translator_config.example.json"; DestDir: "{app}"; DestName: ".translator_config.example.json"; Flags: ignoreversion

[Icons]
Name: "{group}\Traducteur"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Traducteur"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autostartup}\Traducteur"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: startupicon

[InstallDelete]
Type: files; Name: "{autostartup}\Traducteur.lnk"; Check: not WizardIsTaskSelected('startupicon')

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Traducteur"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  BackgroundPage: TInputOptionWizardPage;
  OllamaPage: TInputOptionWizardPage;
  BackgroundPageInitialized: Boolean;

function ConfigPath: String;
begin
  Result := ExpandConstant('{app}\.translator_config.json');
end;

function IsOllamaInstalled: Boolean;
begin
  Result :=
    FileExists(ExpandConstant('{localappdata}\Programs\Ollama\ollama.exe')) or
    (FileSearch('ollama.exe', GetEnv('PATH')) <> '');
end;

function JsonEscape(const Value: String): String;
begin
  Result := Value;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
  StringChangeEx(Result, #13, '\r', True);
  StringChangeEx(Result, #10, '\n', True);
end;

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(
    wpSelectDir,
    'Configuration du modèle',
    'Indiquez comment Traducteur doit joindre le modèle de langage.',
    'Un serveur local ou distant compatible avec l''API Ollama est nécessaire. ' +
      'Ces valeurs seront enregistrées dans .translator_config.json.'
  );
  ConfigPage.Add('Adresse du serveur :', False);
  ConfigPage.Add('Modèle par défaut :', False);
  ConfigPage.Add('Clé API (facultative) :', True);
  ConfigPage.Values[0] := 'http://localhost:11434/api/chat';
  ConfigPage.Values[1] := 'ministral-3:3b';
  ConfigPage.Values[2] := '';

  BackgroundPage := CreateInputOptionPage(
    ConfigPage.ID,
    'Affichage au lancement',
    'Choisissez si la fenêtre doit être visible au lancement.',
    'Ce réglage est indépendant du démarrage automatique avec Windows et peut ' +
      'être modifié plus tard dans .translator_config.json.',
    True,
    True
  );
  BackgroundPage.Add('Afficher la fenêtre au lancement');
  BackgroundPage.Add('Démarrer Traducteur en arrière-plan');
  BackgroundPage.SelectedValueIndex := 0;
  BackgroundPageInitialized := False;

  OllamaPage := CreateInputOptionPage(
    BackgroundPage.ID,
    'Moteur local Ollama',
    'Ollama n''est nécessaire que pour utiliser un modèle sur cet ordinateur.',
    'S''il n''est pas détecté, l''assistant peut télécharger puis lancer son ' +
      'installateur officiel. Choisissez Non si vous utilisez un serveur distant.',
    True,
    False
  );
  OllamaPage.Add('Oui, télécharger et lancer l''installateur officiel Ollama');
  OllamaPage.Add('Non, j''utilise un serveur distant ou je l''installerai plus tard');
  OllamaPage.SelectedValueIndex := 0;
end;

function ConfigurationStartsHidden: Boolean;
var
  Lines: TArrayOfString;
  Index: Integer;
  CompactLine: String;
begin
  Result := False;
  if not LoadStringsFromFile(ConfigPath, Lines) then
    Exit;

  for Index := 0 to GetArrayLength(Lines) - 1 do
  begin
    CompactLine := Lowercase(Lines[Index]);
    StringChangeEx(CompactLine, ' ', '', True);
    StringChangeEx(CompactLine, #9, '', True);
    if Pos('"hide_window_on_start":true', CompactLine) > 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = BackgroundPage.ID) and not BackgroundPageInitialized then
  begin
    if FileExists(ConfigPath) then
    begin
      if ConfigurationStartsHidden then
        BackgroundPage.SelectedValueIndex := 1
      else
        BackgroundPage.SelectedValueIndex := 0;
    end;
    BackgroundPageInitialized := True;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result :=
    ((PageID = ConfigPage.ID) and FileExists(ConfigPath)) or
    ((PageID = OllamaPage.ID) and IsOllamaInstalled);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = ConfigPage.ID then
  begin
    if Trim(ConfigPage.Values[0]) = '' then
    begin
      MsgBox('L''adresse du serveur est obligatoire.', mbError, MB_OK);
      Result := False;
    end
    else if Trim(ConfigPage.Values[1]) = '' then
    begin
      MsgBox('Le modèle par défaut est obligatoire.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure InstallOllamaIfRequested;
var
  OllamaSetupPath: String;
  ResultCode: Integer;
begin
  if WizardSilent or IsOllamaInstalled or (OllamaPage.SelectedValueIndex <> 0) then
    Exit;

  OllamaSetupPath := ExpandConstant('{tmp}\OllamaSetup.exe');
  try
    WizardForm.StatusLabel.Caption := 'Téléchargement de l''installateur officiel Ollama...';
    DownloadTemporaryFile('{#OllamaSetupURL}', 'OllamaSetup.exe', '', nil);
    WizardForm.StatusLabel.Caption := 'Installation d''Ollama...';
    if not Exec(OllamaSetupPath, '', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode) then
      RaiseException('Impossible de lancer l''installateur Ollama.');

    if ResultCode <> 0 then
      MsgBox(
        'L''installateur Ollama s''est terminé avec le code ' + IntToStr(ResultCode) + '.',
        mbInformation,
        MB_OK
      )
    else
      MsgBox(
        'Ollama est installé. Le modèle doit encore être téléchargé avant la première ' +
          'traduction. Ouvrez PowerShell et exécutez :' + #13#10 + #13#10 +
          'ollama pull ' + Trim(ConfigPage.Values[1]),
        mbInformation,
        MB_OK
      );
  except
    MsgBox(
      'L''installation de Traducteur est terminée, mais Ollama n''a pas pu être installé.' +
      Chr(13) + Chr(10) + Chr(13) + Chr(10) + GetExceptionMessage +
      Chr(13) + Chr(10) + Chr(13) + Chr(10) +
      'Vous pouvez le télécharger depuis https://ollama.com/download/windows.',
      mbError,
      MB_OK
    );
  end;
end;

procedure CreateConfiguration;
var
  Lines: TArrayOfString;
  Index: Integer;
  ExamplePath: String;
  HideWindowValue: String;
begin
  if FileExists(ConfigPath) then
    Exit;

  ExamplePath := ExpandConstant('{app}\.translator_config.example.json');
  if not LoadStringsFromFile(ExamplePath, Lines) then
    RaiseException('Impossible de lire le modèle de configuration installé.');

  if BackgroundPage.SelectedValueIndex = 1 then
    HideWindowValue := 'true'
  else
    HideWindowValue := 'false';

  for Index := 0 to GetArrayLength(Lines) - 1 do
  begin
    StringChangeEx(
      Lines[Index],
      '"server_url": "http://localhost:11434/api/chat"',
      '"server_url": "' + JsonEscape(Trim(ConfigPage.Values[0])) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"api_key": ""',
      '"api_key": "' + JsonEscape(ConfigPage.Values[2]) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"default_model": "ministral-3:3b"',
      '"default_model": "' + JsonEscape(Trim(ConfigPage.Values[1])) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"hide_window_on_start": false',
      '"hide_window_on_start": ' + HideWindowValue,
      True
    );
  end;

  if not SaveStringsToUTF8FileWithoutBOM(ConfigPath, Lines, False) then
    RaiseException('Impossible de créer .translator_config.json.');
end;

procedure UpdateBackgroundPreference;
var
  Lines: TArrayOfString;
  Index: Integer;
  HideWindowValue: String;
  Replaced: Boolean;
begin
  if WizardSilent or not FileExists(ConfigPath) then
    Exit;

  if not LoadStringsFromFile(ConfigPath, Lines) then
    Exit;

  if BackgroundPage.SelectedValueIndex = 1 then
    HideWindowValue := 'true'
  else
    HideWindowValue := 'false';

  Replaced := False;
  for Index := 0 to GetArrayLength(Lines) - 1 do
  begin
    if StringChangeEx(
      Lines[Index],
      '"hide_window_on_start": true',
      '"hide_window_on_start": ' + HideWindowValue,
      True
    ) > 0 then
      Replaced := True;
    if StringChangeEx(
      Lines[Index],
      '"hide_window_on_start": false',
      '"hide_window_on_start": ' + HideWindowValue,
      True
    ) > 0 then
      Replaced := True;
    if StringChangeEx(
      Lines[Index],
      '"hide_window_on_start":true',
      '"hide_window_on_start":' + HideWindowValue,
      True
    ) > 0 then
      Replaced := True;
    if StringChangeEx(
      Lines[Index],
      '"hide_window_on_start":false',
      '"hide_window_on_start":' + HideWindowValue,
      True
    ) > 0 then
      Replaced := True;
  end;

  if Replaced then
    SaveStringsToUTF8FileWithoutBOM(ConfigPath, Lines, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if FileExists(ConfigPath) then
      UpdateBackgroundPreference;
    CreateConfiguration;
    InstallOllamaIfRequested;
  end;
end;
