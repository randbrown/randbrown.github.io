---
layout: post
title:  "SQL SMO Scripting Schema and Data"
date:   2018-10-16 17:55:00 -0400
categories: sql
comments: true
---

# Background

I've been using SQL Publishing Wizard ("sqlpubwiz.exe") for probably close to 10 years now.  I use it within my TFS/MSBuild to generate a deployable database script.  
The general algorithm looks like this:

* Clone the DEV database schema to a TEMP database
* Pull in some default data from specific tables of DEV into TEMP
* Perform some fixups on the TEMP database to prepare it for customers.
* Script out both the schema and data from TEMP into a deployable script.

Generally this has worked fairly well.  I've used sqlpubwiz for the first and last parts of this.  However, I recently noticed it had slowed down to an abysmal speed.  I believe this was due to my schema growing and getting more complex.  I tried uninstalling/reinstalling sqlpubwiz, to no avail.

I noticed Microsoft has not released a new version since 1.4, which shipped with Visual Studio 2010. It is bundled with the VS2010 installer,
so you have to install that just to get it!  Gross!

# Enter Powershell

Some googling revealed that most people recommend using either a commercial tool, such as Redgate or Apex, or implementing it yourself with SQL Server Management Objects (SMO) in Powershell.  I decided to create a suitable replacement in Powershell... I did not set out to recreate sqlpubwiz, but just to cover the two use cases I needed.  Specifically, script schema only, or script schema with data.

Now, there are plenty of articles on the web about scripting using SMO in Powershell. So why write this?... 
**Because I found in order to script the data, there are a couple of non-intuitive things you need to do.**

I won't belabor the entire script, as most of it is straight-forward. The full script is in my github repo here: [ScriptDatabase.ps1](https://github.com/randbrown/powershell-tools/blob/master/ScriptDatabase.ps1)

However, I will draw attention to the things I found peculiar.  

1. The [ScriptTransfer](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.transferbase.scripttransfer?view=sqlserver-2016#Microsoft_SqlServer_Management_Smo_TransferBase_ScriptTransfer) method **does not include data**, no matter how hard you try. In fact, if you try to script data with it, it will raise an exception.  So instead, I found you have to use the [EnumScriptTransfer](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.transferbase.enumscripttransfer?view=sqlserver-2016#Microsoft_SqlServer_Management_Smo_TransferBase_EnumScriptTransfer) method instead.
2. The [CopyData](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.transferbase.copydata?view=sqlserver-2016#Microsoft_SqlServer_Management_Smo_TransferBase_CopyData) property **appears to be ignored**.  It seems you have to set the [Options.ScriptData](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.scriptingoptions.scriptdata?view=sqlserver-2016#Microsoft_SqlServer_Management_Smo_ScriptingOptions_ScriptData) instead.

I found both of these by a lot of trial and error :(

```powershell
$transfer = new-object ("$My.Transfer") $db
$transfer.Options.Filename = "$outputFilename"; 
$transfer.CopyData = $includeData # NOTE this seems to be ignored
$transfer.Options.ScriptData = $includeData; # NOTE this is required if you want data scripted!
$transfer.CopySchema = $true
...
$transfer.EnumScriptTransfer() 
```

# Creating a suitable replacement for sqlpubwiz

This was my old sqlpubwiz command used for schema only:
```
sqlpubwiz.exe script -S $(SqlMachineName) -d $(DevSqlDatabaseName) $(BinariesDirectory)\Release\Database\Temp\DBSchema.sql -f -schemaonly
```

This was my old sqlpubwiz command used for schema and data:
```
sqlpubwiz.exe script -S $(SqlMachineName) -d $(ReleaseSqlDatabaseName) $(BinariesDirectory)\Release\Database\DBDeplymentScript.sql -f -nodropexisting
```



My new script command for schema only:
```
powershell .\ScriptDatabase.ps1 $(SqlMachineName) $(DevSqlDatabaseName) $(BinariesDirectory)\Release\Database\Temp\DBSchema.sql
```

My new script command for schema and data:
```
powershell .\ScriptDatabase.ps1 $(SqlMachineName) $(ReleaseSqlDatabaseName) $(BinariesDirectory)\Release\Database\DBDeplymentScript.sql -includeData
```

As you can see, it's not 100% drop-in replacement, but it accepts basically the equivalent arguments.  

#### Performance
One of the reasons I did this was because my sqlpubwiz-based implementation had been growing slower, up to around 15 minutes or even longer on my build server (this includes both schema script, manipulation, and then the final schema+data script).
When I tried installing sqlpubwiz on another computer, I couldn't even get it working - it failed with an IndexOutOfBoundsException.  
I presume it has to do with VS2010 prerequisites or some such.  At any rate, I knew the days were numbered with the sqlpubwiz approach,
and decided to tackle the problem. 

After having done this, my new powershell-SMO-based build runs in about 3 minutes (again, this includes all steps mentioned above).  

# Wrap Up
I wrote this article and published my script because I couldn't find any other articles online which addressed my specific use cases.
While there are several that show how to script the schema, and several showing how to use the 
[TransferData](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.transfer.transferdata?view=sqlserver-2016#Microsoft_SqlServer_Management_Smo_Transfer_TransferData) method to transfer 
data directly without scripting it, I did not run across any others showing my use case of scripting the data into a file.
By writing this article, _hopefully_ I'll be more likely to remember it myself, and perhaps it could help someone else who gets stuck
in the same situation.


#### References

* [SQL Publishing Wizard 1.1](https://www.microsoft.com/en-us/download/details.aspx?id=5498)
* [Transfer Class (SMO)](https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.management.smo.transfer?view=sqlserver-2016)
* [Powershell-tools](https://github.com/randbrown/powershell-tools)
