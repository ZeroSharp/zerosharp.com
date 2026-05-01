+++
title = "How to recursively change file ownership"
date = 2013-02-28T17:40:00+01:00
slug = "how-to-recursively-change-file-ownership"
categories = ["powershell", "windows"]
description = "A powershell script to recursively change the ownership of files in the current and subdirectories."
disqus_identifier = "http://ZeroSharp.github.com/how-to-recursively-change-file-ownership/"
disqus_url        = "http://ZeroSharp.github.com/how-to-recursively-change-file-ownership/"
+++
I recently ran into some file ownership trouble after cloning a bitbucket repository. 

The following script saved my bacon.

```powershell
# FixOwnership.ps1
# This script recursively fixes the ownership on the files in the 
# current and subdirectories.

$acct1 = New-Object System.Security.Principal.NTAccount('Administrators')
$profilefolder = Get-Item .
$acl1 = $profilefolder.GetAccessControl()
$acl1.SetOwner($acct1)
dir -r . | set-acl -aclobject $acl1
pause
```
