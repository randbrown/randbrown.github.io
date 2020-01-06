---
layout: post
title:  "Setting up Windows Terminal"
date:   2020-01-06 17:20:00 -0500
categories: windows terminal powershell
comments: true
---

I've been using [Windows Terminal](https://github.com/microsoft/terminal)  recently.  It's quite nice! 
It took me a while to get it set up the way I like it, with some non-obvious hurdles,
so I decided to document it in a post.

![Windows Terminal](/assets/pics/wt_randbrown.jpg "Windows Terminal"){: .image-flow .image-25 .right} 

I started with this excellent post by [Scott Hanselman](https://www.hanselman.com/blog/HowToMakeAPrettyPromptInWindowsTerminalWithPowerlineNerdFontsCascadiaCodeWSLAndOhmyposh.aspx)
about getting it installed and set up with some nice tools such as
POSH-GIT, OH-MY-POSH, and nice fonts.

*Note*: I'm using [UbuntuMono NF](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/UbuntuMono) instead of the Delugia as described in Hanselman's post, but either works and looks nice.

But, it was still missing the option to "Open Windows Terminal Here" from Windows Explorer, which I was used to having with CMD and Powershell... 

## Opening Windows Terminal Here in Windows Explorer

As of this writing, WT does not offer an easy way to open a terminal from Windows Explorer at a specific folder.
The closest thing is the shortcut described [here](https://github.com/microsoft/terminal/issues/878):
where you navigate to the folder in Explorer, then type in `wt` into the address bar to launch a terminal there.  
That is *nice to have*, but not particularly a *great user experience* in my opinion,
since I have been used to the context menu for years and would prefer to keep that approach.

### Adding "Terminal Here" to the registry.  

This can be done, somewhat similarly as it was for CMD and Powershell (but with a catch),
by adding the following to the registry:

```registry

Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\shell\Open WT Here]
@="Terminal Here"

[HKEY_CLASSES_ROOT\Directory\shell\Open WT Here\command]
@="C:\\Windows\\System32\\cmd.exe /c cd %1 && start \"\" wt.exe"

```

This *should* be straightforward, *except* wt.exe does not allow command line parameters. 
So we can't simply call `wt.exe %1` to pass in the folder like we would have done with PS or CMD. 
Instead, we have to invoke `cmd.exe` in order to change to the `%1` folder, and then start the `wt.exe` application. 

This gets us the context menu!  

![Terminal Here Context Menu](/assets/pics/wt_context_menu.jpg "Terminal Here Context Menu"){:  } 


*BUT* this alone will not quite work, however..... 
If you try it like this, you'll get your context menu and you can use it to launch a WT window, 
BUT you'll still land in your default folder instead of the target folder.  This is because by default, 
WT does not care what the working folder is when it initializes....

# The Starting Directory

By default, WT starts in your `$HOME` folder.  Alternatively, you can configure a folder in your profiles.json by using the `startingDirectory` property.  However, in our case we want to use the current working folder.  So to get WT to use the working folder, you must specify `"startingDirectory": "."` in the profile. This gives the desired result.

```javascript

{
    "$schema": "https://aka.ms/terminal-profiles-schema",

    "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",

    "profiles":
    [
        {
            // Make changes here to the powershell.exe profile
            "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
            "name": "Windows PowerShell",
            "commandline": "powershell.exe",
            "hidden": false,

            // "startingDirectory": "." is used in order to observe the 'start in' of a windows shortcut, etc
            "startingDirectory": ".",

            "fontFace":  "UbuntuMono NF"
        },
        ///...
    ]
}
```

However, that leaves us with this problem:  when starting WT normally from the start menu, it will be in the `C:\windows\system32` folder, which is rarely helpful.  So next we work around that....

# Checking for a reasonable default working folder:

I don't ever want to start a shell in system32.  So we go to the powershell profile (e.g. $HOME/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1) and add some logic (*I added this at the end of my profile ps1 file*):

```powershell

# we never want to start win system32. If not already in a good location, move to $HOME
"working path "  + (Get-Location).Path
if ((Get-Location).Path -eq "/mnt/c/Windows/System32" -or (Get-Location).Path -eq "C:\WINDOWS\system32" ) {
	Set-Location ~ 
  "working path changed to "  + (Get-Location).Path
}

```

Here we print the current path just for good measure.  Then we check to see if it's the system32 folder, 
either in the normal path or in the WSL mounted filesystem just in case this gets called from there.  
If so, I set the location to the home folder using the tilde (`~`) short hand.  
Of course I could have used any folder here, but I figured `$HOME` is a good choice since it's the
default folder anyway.

Now this properly handles the case of when I launch WT from the start menu or shortcut.  
And it still respects the working folder in the case where it is launched from the Explorer context menu.  Yay!

