+++
title = "Hello, Hugo"
date = 2026-05-01T20:00:00+01:00
slug = "hello-hugo"
categories = ["meta", "site"]
+++

A short test post to verify the new Hugo build of ZeroSharp.

Inline code looks like `Session.Delete(ICollection objects)` and stays on the body line. Fenced code blocks render through Chroma with the Solarized Dark theme:

```csharp
public static class SessionExtensions
{
    public static ModificationResult Delete<T>(this Session session, CriteriaOperator criteria = null)
        where T : IXPObject
    {
        if (ReferenceEquals(criteria, null))
            criteria = CriteriaOperator.Parse("True");

        XPClassInfo classInfo = session.GetClassInfo(typeof(T));
        var batchWideData = new BatchWideDataHolder4Modification(session);
        // ...
        return session.DataLayer.ModifyData(collectionToArray);
    }
}
```

Lists, **emphasis**, and links to [the GitHub repo](https://github.com/zerosharp) all use the brand purple with a teal hover.

That's it — if you can see this with the right typography, palette, and dark code frame, the bones of the new site are in place.
