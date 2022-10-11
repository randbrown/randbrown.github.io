---
layout: post
title:  "WebClient and Redirects"
date:   2022-10-11 16:48:00 -0400
categories: webclient postman
comments: true
---

I have some code to make a web request using [WebClient.DownloadString](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstring?view=net-6.0),
do some processing, then insert into my database.   Standard stuff.  But today I hit an odd problem which took me quite some time to figure out:

**Automatic redirection in WebClient does *not* include the Authorization header!**

In my case, the URL I needed was of the form:

`https://foo.bar/api/something/?p1=baz&p2=bar`

and the API requires an Authorization header such as:

`Authorization: Token abcdefg...12345`

My code is configuration driven, so normally I just plug in the URL and header strings into the configuration and everything just works.  However, due to a simple error, I omitted the trailing slash, like so:

`https://foo.bar/something?p1=baz&p2=bar`

At a glance this would seem fine.  In my tests with [Postman](https://www.postman.com/), it worked flawlessly, so I plugged the URL into my app and figured I was on my way to lunch. 

But instead, in my app code I get a response from the API:

`401: {"detail":"Authentication credentials were not provided."}`

What?  So I recheck my header.  It's right.  I check again.  And again.  I even copied the header straight out of Postman (which works), but my code still fails.  After scratching my head a while I opened up [Fiddler](https://www.telerik.com/download/fiddler) and took a closer look.

I realized there was a 301 redirect happening, from the API, to redirect me to the proper URL which includes the trailing slash.  Turns out, Postman was quietly handling this.  My code, as it turns out, was indeed following the redirect, however, there is one crucial behavior which I was not aware of until today.

The [WebClient.AllowAutoRedirect property](https://learn.microsoft.com/en-us/dotnet/api/system.net.httpwebrequest.allowautoredirect) clears the Authorization upon redirects!  

Now that I realize this, I know how to handle it if it ever pops up in the future.  But for now, the obvious and simple answer is to fix the URL - and avoid the redirect altogether!

## Observations/Notes
I noticed the other headers I set remained on the redirect, but sure enough, the Authorization header was gone.  I totally understand why you'd want to clear the Authorization header when redirecting to another domain, as that's an obvious security hole.  But it seems to me a redirect within the same scheme/domain such as this would make sense to keep the header. I'd love to hear any insight as to what the security implications of that would be.  
