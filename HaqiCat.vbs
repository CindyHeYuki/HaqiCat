Option Explicit

Dim shell, fileSystem, projectRoot, pythonWindow, command, argument

Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

projectRoot = fileSystem.GetParentFolderName(WScript.ScriptFullName)
pythonWindow = projectRoot & "\.venv\Scripts\pythonw.exe"

If Not fileSystem.FileExists(pythonWindow) Then
    MsgBox "HaqiCat environment is missing. Install dependencies first.", _
        vbCritical, "HaqiCat"
    WScript.Quit 1
End If

shell.CurrentDirectory = projectRoot
shell.Environment("Process")("PYTHONPATH") = projectRoot & "\src"

command = Chr(34) & pythonWindow & Chr(34) & " -m haqicat"
For Each argument In WScript.Arguments
    command = command & " " & Chr(34) & _
        Replace(argument, Chr(34), Chr(34) & Chr(34)) & Chr(34)
Next

shell.Run command, 0, False
