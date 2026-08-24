#define MyAppName "Traducteur"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Sylvain Vuilleumier"
#define MyAppURL "https://gitlab.epfl.ch/sisb-public/id/traducteur"
#define MyAppExeName "traducteur.exe"
#define OllamaSetupURL "https://ollama.com/download/OllamaSetup.exe"
#define AppMutexName "TraducteurAppMutex-8E28A203-8A35-4F78-BE6B-FD0718E146AD"
#define SetupMutexName "TraducteurSetupMutex-8E28A203-8A35-4F78-BE6B-FD0718E146AD"
#ifndef MyAppExeSource
#define MyAppExeSource "..\bin\traducteur.exe"
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
SetupMutex={#SetupMutexName}
CloseApplications=yes
RestartApplications=no
OutputDir=..\bin
OutputBaseFilename=traducteur-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
LicenseFile=..\LICENSE
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion=1.1.0.0
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
Name: "{group}\Désinstaller Traducteur"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Traducteur"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autostartup}\Traducteur"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: startupicon

[InstallDelete]
Type: files; Name: "{autostartup}\Traducteur.lnk"; Check: not WizardIsTaskSelected('startupicon')

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Traducteur"; Flags: nowait postinstall skipifsilent

[Code]
var
  ExistingInstallPage: TInputOptionWizardPage;
  KeepConfigurationCheckBox: TNewCheckBox;
  EnvironmentPage: TInputOptionWizardPage;
  ConfigPage: TInputQueryWizardPage;
  ApiFormatPage: TInputOptionWizardPage;
  BackgroundPage: TInputOptionWizardPage;
  OllamaPage: TInputOptionWizardPage;
  BackgroundPageInitialized: Boolean;
  ExistingInstallationFound: Boolean;
  ExistingUninstaller: String;
  ExistingInstallLocation: String;
  CleanReinstallCompleted: Boolean;
  UninstallOnlyCompleted: Boolean;
  DeleteUserDataOnUninstall: Boolean;
  LastEnvironmentSelection: Integer;
  LastApiFormatSelection: Integer;

function ConfigPath: String;
begin
  Result := ExpandConstant('{app}\.translator_config.json');
end;

function StatePath: String;
begin
  Result := ExpandConstant('{app}\.translator_state.json');
end;

function DetectExistingInstallation: Boolean;
var
  RegistryKey: String;
  DefaultLocation: String;
begin
  Result := False;
  ExistingUninstaller := '';
  ExistingInstallLocation := '';
  RegistryKey :=
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8E28A203-8A35-4F78-BE6B-FD0718E146AD}_is1';

  if RegQueryStringValue(HKCU, RegistryKey, 'UninstallString', ExistingUninstaller) then
  begin
    RegQueryStringValue(HKCU, RegistryKey, 'InstallLocation', ExistingInstallLocation);
    Result := True;
  end
  else if RegQueryStringValue(HKLM, RegistryKey, 'UninstallString', ExistingUninstaller) then
  begin
    RegQueryStringValue(HKLM, RegistryKey, 'InstallLocation', ExistingInstallLocation);
    Result := True;
  end
  else if RegQueryStringValue(HKLM64, RegistryKey, 'UninstallString', ExistingUninstaller) then
  begin
    RegQueryStringValue(HKLM64, RegistryKey, 'InstallLocation', ExistingInstallLocation);
    Result := True;
  end;

  DefaultLocation := ExpandConstant('{userpf}\Traducteur');
  if Result and (ExistingInstallLocation = '') then
    ExistingInstallLocation := DefaultLocation;
  if not Result and
    (FileExists(AddBackslash(DefaultLocation) + '{#MyAppExeName}') or
     FileExists(AddBackslash(DefaultLocation) + '.translator_config.json')) then
  begin
    ExistingInstallLocation := DefaultLocation;
    ExistingUninstaller := AddBackslash(DefaultLocation) + 'unins000.exe';
    Result := True;
  end;
end;

function CleanReinstallRequested: Boolean;
begin
  Result := ExistingInstallationFound and
    (ExistingInstallPage.SelectedValueIndex = 0);
end;

function KeepConfigurationRequested: Boolean;
begin
  Result := KeepConfigurationCheckBox.Checked;
end;

function ReplaceConfigurationRequested: Boolean;
begin
  Result := CleanReinstallRequested and not KeepConfigurationRequested;
end;

function UninstallOnlyRequested: Boolean;
begin
  Result := ExistingInstallationFound and
    (ExistingInstallPage.SelectedValueIndex = 1);
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
  ExistingInstallationFound := DetectExistingInstallation;
  CleanReinstallCompleted := False;
  UninstallOnlyCompleted := False;
  LastEnvironmentSelection := -1;
  LastApiFormatSelection := -1;

  ExistingInstallPage := CreateInputOptionPage(
    wpWelcome,
    'Traducteur est déjà installé',
    'Choisissez l''opération à effectuer.',
    'La configuration peut être conservée pour une prochaine utilisation.',
    True,
    False
  );
  ExistingInstallPage.Add('Réinstaller l''application');
  ExistingInstallPage.Add('Désinstaller l''application');
  ExistingInstallPage.SelectedValueIndex := 0;

  KeepConfigurationCheckBox := TNewCheckBox.Create(ExistingInstallPage);
  KeepConfigurationCheckBox.Parent := ExistingInstallPage.Surface;
  KeepConfigurationCheckBox.Left := 0;
  KeepConfigurationCheckBox.Top := ScaleY(72);
  KeepConfigurationCheckBox.Width := ExistingInstallPage.SurfaceWidth;
  KeepConfigurationCheckBox.Caption :=
    'Conserver la configuration et le dernier modèle utilisé';
  KeepConfigurationCheckBox.Checked := True;

  EnvironmentPage := CreateInputOptionPage(
    wpSelectDir,
    'Environnement d''utilisation',
    'Choisissez le service auquel vous avez accès.',
    'Le service RCP est réservé aux membres de l''EPFL.',
    True,
    False
  );
  EnvironmentPage.Add('EPFL (Service RCP)');
  EnvironmentPage.Add('Autre serveur');
  EnvironmentPage.SelectedValueIndex := 0;

  ApiFormatPage := CreateInputOptionPage(
    EnvironmentPage.ID,
    'Service de modèle',
    'Choisissez le service utilisé par Traducteur.',
    '',
    True,
    False
  );
  ApiFormatPage.Add('Ollama');
  ApiFormatPage.Add('OpenAI / vLLM');
  ApiFormatPage.SelectedValueIndex := 0;

  ConfigPage := CreateInputQueryPage(
    ApiFormatPage.ID,
    'Configuration du serveur',
    'Vérifiez les paramètres de connexion proposés.',
    'Les URL peuvent être modifiées si votre serveur utilise des adresses différentes.'
  );
  ConfigPage.Add('URL exacte d''inférence :', False);
  ConfigPage.Add('URL de liste des modèles (facultative) :', False);
  ConfigPage.Add('Modèle par défaut (facultatif) :', False);
  ConfigPage.Add('Clé API (facultative) :', True);
  ConfigPage.Values[0] := 'http://localhost:11434/api/chat';
  ConfigPage.Values[1] := 'http://localhost:11434/api/tags';
  ConfigPage.Values[2] := '';
  ConfigPage.Values[3] := '';

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

procedure InitializeEndpointFields;
begin
  if EnvironmentPage.SelectedValueIndex = 0 then
    ApiFormatPage.SelectedValueIndex := 1;

  if (LastEnvironmentSelection = EnvironmentPage.SelectedValueIndex) and
    (LastApiFormatSelection = ApiFormatPage.SelectedValueIndex) then
    Exit;

  if EnvironmentPage.SelectedValueIndex = 0 then
  begin
    ConfigPage.Values[0] :=
      'https://inference.rcp.epfl.ch/v1/chat/completions';
    ConfigPage.Values[1] := 'https://inference.rcp.epfl.ch/v1/models';
    ConfigPage.Values[2] := 'swiss-ai/Apertus-v1.5-8B';
    ConfigPage.Values[3] := '';
    ConfigPage.PromptLabels[3].Caption := 'Clé API RCP :';
  end
  else if ApiFormatPage.SelectedValueIndex = 0 then
  begin
    ConfigPage.Values[0] := 'http://localhost:11434/api/chat';
    ConfigPage.Values[1] := 'http://localhost:11434/api/tags';
    ConfigPage.Values[2] := '';
    ConfigPage.Values[3] := '';
    ConfigPage.PromptLabels[3].Caption := 'Clé API (facultative) :';
  end
  else
  begin
    ConfigPage.Values[0] := '';
    ConfigPage.Values[1] := '';
    ConfigPage.Values[2] := '';
    ConfigPage.Values[3] := '';
    ConfigPage.PromptLabels[3].Caption := 'Clé API (facultative) :';
  end;
  LastEnvironmentSelection := EnvironmentPage.SelectedValueIndex;
  LastApiFormatSelection := ApiFormatPage.SelectedValueIndex;
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

function ConfigurationUsesOpenAI: Boolean;
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
    if Pos('"api_format":"openai"', CompactLine) > 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = ConfigPage.ID then
    InitializeEndpointFields;

  if (CurPageID = BackgroundPage.ID) and not BackgroundPageInitialized then
  begin
    if FileExists(ConfigPath) and not ReplaceConfigurationRequested then
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
    ((PageID = ExistingInstallPage.ID) and not ExistingInstallationFound) or
    ((PageID = EnvironmentPage.ID) and FileExists(ConfigPath) and
      not ReplaceConfigurationRequested) or
    ((PageID = ConfigPage.ID) and FileExists(ConfigPath) and
      not ReplaceConfigurationRequested) or
    ((PageID = ApiFormatPage.ID) and FileExists(ConfigPath) and
      not ReplaceConfigurationRequested) or
    ((PageID = ApiFormatPage.ID) and
      (EnvironmentPage.SelectedValueIndex = 0)) or
    ((PageID = OllamaPage.ID) and
      (IsOllamaInstalled or (ApiFormatPage.SelectedValueIndex <> 0) or
       (FileExists(ConfigPath) and not ReplaceConfigurationRequested and
        ConfigurationUsesOpenAI)));
end;

function WaitForTraducteurToClose(TimeoutMilliseconds: Integer): Boolean;
var
  WaitedMilliseconds: Integer;
begin
  WaitedMilliseconds := 0;
  while CheckForMutexes('{#AppMutexName}') and
    (WaitedMilliseconds < TimeoutMilliseconds) do
  begin
    Sleep(200);
    WaitedMilliseconds := WaitedMilliseconds + 200;
  end;
  Result := not CheckForMutexes('{#AppMutexName}');
end;

function CloseRunningTraducteur: Boolean;
var
  ApplicationPath: String;
  ResultCode: Integer;
begin
  Result := True;
  if not CheckForMutexes('{#AppMutexName}') then
    Exit;

  if not WizardSilent and (MsgBox(
    'Traducteur est actuellement lancé.' + #13#10 + #13#10 +
      'Voulez-vous que l''installateur l''arrête automatiquement ?' + #13#10 +
      'Les textes non enregistrés dans la fenêtre seront perdus.',
    mbConfirmation,
    MB_YESNO
  ) <> IDYES) then
  begin
    Result := False;
    Exit;
  end;

  ApplicationPath := ExpandConstant('{app}\{#MyAppExeName}');
  if not FileExists(ApplicationPath) and (ExistingInstallLocation <> '') then
    ApplicationPath := AddBackslash(ExistingInstallLocation) + '{#MyAppExeName}';

  if FileExists(ApplicationPath) then
  begin
    Exec(
      ApplicationPath,
      '--shutdown --hidden',
      ExtractFileDir(ApplicationPath),
      SW_HIDE,
      ewWaitUntilTerminated,
      ResultCode
    );
  end;

  if WaitForTraducteurToClose(5000) then
    Exit;

  if not Exec(
    ExpandConstant('{sys}\taskkill.exe'),
    '/F /T /IM {#MyAppExeName}',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) then
  begin
    Result := False;
    Exit;
  end;

  Result := WaitForTraducteurToClose(5000);
end;

procedure DeleteConfigurationFrom(const InstallLocation: String);
begin
  if InstallLocation = '' then
    Exit;
  DeleteFile(AddBackslash(InstallLocation) + '.translator_config.json');
  DeleteFile(AddBackslash(InstallLocation) + '.translator_state.json');
end;

function RunExistingUninstaller(PreserveConfiguration: Boolean): Boolean;
var
  UninstallerPath: String;
  ResultCode: Integer;
  ExistingConfigPath: String;
  ExistingStatePath: String;
  ConfigBackupPath: String;
  StateBackupPath: String;
  ConfigWasPresent: Boolean;
  StateWasPresent: Boolean;
begin
  Result := False;
  UninstallerPath := RemoveQuotes(ExistingUninstaller);
  if not FileExists(UninstallerPath) then
  begin
    MsgBox(
      'Le désinstalleur de la version existante est introuvable. Utilisez la page ' +
        'Applications installées de Windows pour supprimer Traducteur.',
      mbError,
      MB_OK
    );
    Exit;
  end;

  ExistingConfigPath := AddBackslash(ExistingInstallLocation) +
    '.translator_config.json';
  ExistingStatePath := AddBackslash(ExistingInstallLocation) +
    '.translator_state.json';
  ConfigBackupPath := ExpandConstant('{tmp}\traducteur-config-backup.json');
  StateBackupPath := ExpandConstant('{tmp}\traducteur-state-backup.json');
  ConfigWasPresent := FileExists(ExistingConfigPath);
  StateWasPresent := FileExists(ExistingStatePath);

  if PreserveConfiguration and ConfigWasPresent and not CopyFile(
    ExistingConfigPath,
    ConfigBackupPath,
    False
  ) then
  begin
    MsgBox(
      'La configuration n''a pas pu être sauvegardée. La désinstallation est annulée ' +
        'pour éviter toute perte de réglages.',
      mbError,
      MB_OK
    );
    Exit;
  end;
  if PreserveConfiguration and StateWasPresent and not CopyFile(
    ExistingStatePath,
    StateBackupPath,
    False
  ) then
  begin
    MsgBox(
      'L''état de l''application n''a pas pu être sauvegardé. La désinstallation est ' +
        'annulée pour éviter toute perte de réglages.',
      mbError,
      MB_OK
    );
    Exit;
  end;

  WizardForm.StatusLabel.Caption := 'Désinstallation de Traducteur...';
  if not Exec(
    UninstallerPath,
    '/SILENT /SUPPRESSMSGBOXES /NORESTART',
    ExtractFileDir(UninstallerPath),
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) or (ResultCode <> 0) then
  begin
    MsgBox(
      'Traducteur n''a pas pu être désinstallé. Code retourné : ' +
        IntToStr(ResultCode) + '.',
      mbError,
      MB_OK
    );
    Exit;
  end;

  if PreserveConfiguration then
  begin
    if ConfigWasPresent or StateWasPresent then
      ForceDirectories(ExistingInstallLocation);
    if ConfigWasPresent and not CopyFile(
      ConfigBackupPath,
      ExistingConfigPath,
      False
    ) then
    begin
      MsgBox(
        'L''application a été désinstallée, mais sa configuration n''a pas pu être ' +
          'restaurée automatiquement. Une copie reste disponible dans le dossier ' +
          'temporaire de l''installateur.',
        mbError,
        MB_OK
      );
      Exit;
    end;
    if StateWasPresent and not CopyFile(
      StateBackupPath,
      ExistingStatePath,
      False
    ) then
    begin
      MsgBox(
        'L''application a été désinstallée, mais le dernier modèle mémorisé n''a pas pu ' +
          'être restauré automatiquement.',
        mbError,
        MB_OK
      );
      Exit;
    end;
  end
  else
  begin
    DeleteConfigurationFrom(ExistingInstallLocation);
    DeleteConfigurationFrom(ExpandConstant('{app}'));
  end;

  Result := True;
end;

function RunCleanReinstall: Boolean;
begin
  Result := True;
  if CleanReinstallCompleted or not CleanReinstallRequested then
    Exit;

  Result := RunExistingUninstaller(KeepConfigurationRequested);
  if Result then
    CleanReinstallCompleted := True;
end;

function RunUninstallOnly: Boolean;
begin
  Result := False;
  if UninstallOnlyCompleted then
  begin
    Result := True;
    Exit;
  end;

  if not CloseRunningTraducteur then
    Exit;

  Result := RunExistingUninstaller(KeepConfigurationRequested);
  if Result then
    UninstallOnlyCompleted := True;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if not CloseRunningTraducteur then
  begin
    Result :=
      'Traducteur doit être fermé avant de poursuivre. Fermez-le depuis son icône ' +
      'dans la barre système, puis relancez l''installation.';
    Exit;
  end;

  if not RunCleanReinstall then
    Result :=
      'La version existante n''a pas pu être désinstallée. ' +
      'Utilisez son désinstalleur puis relancez cette installation.';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = ExistingInstallPage.ID) and UninstallOnlyRequested then
  begin
    if MsgBox(
      'Traducteur va être désinstallé.' + #13#10 + #13#10 +
        'Continuer ?',
      mbConfirmation,
      MB_YESNO
    ) <> IDYES then
    begin
      Result := False;
      Exit;
    end;

    if RunUninstallOnly then
    begin
      if KeepConfigurationRequested then
        MsgBox(
          'Traducteur a été désinstallé. Sa configuration a été conservée.',
          mbInformation,
          MB_OK
        )
      else
        MsgBox(
          'Traducteur et sa configuration ont été désinstallés.',
          mbInformation,
          MB_OK
        );
      WizardForm.Close;
    end;
    Result := False;
    Exit;
  end;

  if CurPageID = ConfigPage.ID then
  begin
    if Trim(ConfigPage.Values[0]) = '' then
    begin
      MsgBox('L''URL exacte d''inférence est obligatoire.', mbError, MB_OK);
      Result := False;
    end
    else if (Trim(ConfigPage.Values[1]) = '') and (Trim(ConfigPage.Values[2]) = '') then
    begin
      MsgBox(
        'Indiquez une URL de liste des modèles ou un modèle par défaut.',
        mbError,
        MB_OK
      );
      Result := False;
    end;
    if Result and (EnvironmentPage.SelectedValueIndex = 0) and
      (Trim(ConfigPage.Values[3]) = '') then
    begin
      MsgBox(
        'Une clé API RCP est nécessaire. Créez-la sur :' + #13#10 + #13#10 +
          'https://portal.rcp.epfl.ch/aiaas/keys',
        mbError,
        MB_OK
      );
      Result := False;
    end;
  end;
end;

procedure InstallOllamaIfRequested;
var
  OllamaSetupPath: String;
  ResultCode: Integer;
begin
  if WizardSilent or (ApiFormatPage.SelectedValueIndex <> 0) or
    IsOllamaInstalled or (OllamaPage.SelectedValueIndex <> 0) then
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
    else if Trim(ConfigPage.Values[2]) <> '' then
    begin
      MsgBox(
        'Ollama est installé. Le modèle doit encore être téléchargé avant la première ' +
          'traduction. Ouvrez PowerShell et exécutez :' + #13#10 + #13#10 +
          'ollama pull ' + Trim(ConfigPage.Values[2]),
        mbInformation,
        MB_OK
      );
    end
    else
    begin
      MsgBox(
        'Ollama est installé. Installez au moins un modèle avec ollama pull, puis ' +
          'sélectionnez-le dans Traducteur.',
        mbInformation,
        MB_OK
      );
    end;
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
  ApiFormatValue: String;
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

  if ApiFormatPage.SelectedValueIndex <> 0 then
    ApiFormatValue := 'openai'
  else
    ApiFormatValue := 'ollama';

  for Index := 0 to GetArrayLength(Lines) - 1 do
  begin
    StringChangeEx(
      Lines[Index],
      '"api_format": "ollama"',
      '"api_format": "' + ApiFormatValue + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"server_url": "http://localhost:11434/api/chat"',
      '"server_url": "' + JsonEscape(Trim(ConfigPage.Values[0])) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"models_url": "http://localhost:11434/api/tags"',
      '"models_url": "' + JsonEscape(Trim(ConfigPage.Values[1])) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"api_key": ""',
      '"api_key": "' + JsonEscape(ConfigPage.Values[3]) + '"',
      True
    );
    StringChangeEx(
      Lines[Index],
      '"default_model": "ministral-3:3b"',
      '"default_model": "' + JsonEscape(Trim(ConfigPage.Values[2])) + '"',
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

function InitializeUninstall: Boolean;
begin
  Result := True;
  DeleteUserDataOnUninstall := SuppressibleMsgBox(
    'Voulez-vous également supprimer la configuration de Traducteur et le dernier ' +
      'modèle mémorisé ?' + #13#10 + #13#10 +
      'Choisissez Non pour conserver ces réglages en vue d''une réinstallation.',
    mbConfirmation,
    MB_YESNO,
    IDNO
  ) = IDYES;
end;

procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if UninstallOnlyCompleted then
    Confirm := False;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if (CurUninstallStep = usPostUninstall) and DeleteUserDataOnUninstall then
  begin
    DeleteFile(ExpandConstant('{app}\.translator_config.json'));
    DeleteFile(ExpandConstant('{app}\.translator_state.json'));
  end;
end;
