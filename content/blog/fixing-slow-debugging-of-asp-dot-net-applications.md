+++
title = "Fixing slow debugging of ASP.NET applications"
date = 2015-06-03T21:31:00+01:00
slug = "fixing-slow-debugging-of-asp-dot-net-applications"
categories = ["c#", "visual studio", "devexpress", "xaf"]
description = "Disabling Visual Studio's Browser Link feature improves the debugging experience."
disqus_identifier = "http://ZeroSharp.github.com/fixing-slow-debugging-of-asp-dot-net-applications/"
disqus_url        = "http://ZeroSharp.github.com/fixing-slow-debugging-of-asp-dot-net-applications/"
+++
For a while I've noticed an annoying slowness when debugging ASP.NET applications from Visual Studio. Just after every page load it takes about a second before the buttons become clickable. I noticed mostly when debugging XAF applications, perhaps because the pages are quite complex.

Turns out the culprit is something called [Browser Link](http://www.asp.net/visual-studio/overview/2013/using-browser-link) which was introduced in Visual Studio 2013. It's enabled by default.

To turn it off you can turn it off from the menu:

![](/images/blog/browserlink-001.png)

Or you can add the following to your web.config file.
```xml
<appSettings>
  <add key="vs:EnableBrowserLink" value="false"/>
</appSettings>
```
