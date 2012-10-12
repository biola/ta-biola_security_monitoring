' # Copyright 2012, Biola University 
' #
' # Licensed under the Apache License, Version 2.0 (the "License");
' # you may not use this file except in compliance with the License.
' # You may obtain a copy of the License at
' #
' # http://www.apache.org/licenses/LICENSE-2.0
' #
' # Unless required by applicable law or agreed to in writing, software
' # distributed under the License is distributed on an "AS IS" BASIS,
' # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
' # See the License for the specific language governing permissions and
' # limitations under the License.
' #
'
' Script below should report back on security and non-security updates,
' geared towards automatic field extraction in Splunk.
'
' TODO: Could also add in registry checking for auto-update stats
' e.g. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\Results\<Detect or Install>\LastSuccessTime
'

Set updateSession = CreateObject("Microsoft.Update.Session")
updateSession.ClientApplicationID = "Scripted Update Check"

Set updateSearcher = updateSession.CreateUpdateSearcher()


Set searchResult = updateSearcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")


Dim numberOfUpdatesPendingReboot
Dim numberOfPendingSecurityUpdates
Dim numberOfPendingNonSecurityUpdates
numberOfUpdatesPendingReboot = 0
numberOfPendingSecurityUpdates = 0
numberOfPendingNonSecurityUpdates = 0

For I = 0 To searchResult.Updates.Count-1
    Set update = searchResult.Updates.Item(I)
    If update.MsrcSeverity = "Critical" Or update.MsrcSeverity = "Important" Or update.MsrcSeverity = "Moderate" Or update.MsrcSeverity = "Low" Then
	    numberOfPendingSecurityUpdates = numberOfPendingSecurityUpdates + 1
	    If update.InstallationBehavior.RebootBehavior > 0 Then
		numberOfUpdatesPendingReboot = numberOfUpdatesPendingReboot + 1
	    End If
	    WScript.Echo now & " AvailableSecurityUpdate=" & Chr(34) & update.Title & Chr(34) & " Severity=" & update.MsrcSeverity
    Else
	    WScript.Echo now & " AvailableNonSecurityUpdate=" & Chr(34) & update.Title & Chr(34)
	    numberOfPendingNonSecurityUpdates = numberOfPendingNonSecurityUpdates + 1
    End If
Next

WScript.Echo now & " NumberOfPendingSecurityUpdates=" & numberOfPendingSecurityUpdates & " NumberOfUpdatesPendingReboot=" & numberOfUpdatesPendingReboot & " NumberOfPendingNonSecurityUpdates=" & numberOfPendingNonSecurityUpdates

Set objSysInfo = CreateObject("Microsoft.Update.SystemInfo")
If objSysInfo.RebootRequired Then
  Wscript.Echo now & " WindowsRebootRequired=true"
End If
