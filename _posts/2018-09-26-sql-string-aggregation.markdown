---
layout: post
title:  "SQL String Aggregation"
date:   2018-09-26 17:00:00 -0400
categories: sql
comments: true
---

<style type="text/css">
table{
    table-layout:fixed;
    width:100%;
    border-collapse: collapse;
}
td,th{
    border:1px solid #000;
}
tr td:last-child{
    width:1%;
    word-wrap:break-word
}
</style>

I recently needed to aggregate a list of related records in SQL Server.  Given each *parent* record, I want to show a comma-separated list of a *distinct grandchild* record column.

In my application I needed to list configured time intervals for each parent air pollution parameter, based on an intermediate configuration table.  However, for the sake of demonstration, I'll concoct a similar example using the [WideWorldImporters  sample database for SQL Server](https://github.com/Microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers) instead.

Given the relation between Orders, Order Lines, and Package Types, let's build a query to show which types of packages are needed for each order.  

![Order Package Types](/assets/pics/wwi_orderpackagetypes_annotated.png "Order Package Types"){: .image-flow .image-25 .right} 

And to note, there may be multiple lines per order of each package, type so we want a DISTINCT list of package types for each order.  
E.g.  If Order 1 contains three lines of type Packet, we only want to return "Packet" once.

I've done similar things in the past, but only for one-off queries I was running in SSMS. In those cases, I've used a temporary variable,
and the COALESCE operator to select into the variable.  However, this time, I needed to add it to a view, so I needed to find a way
to do so without the use of a temporary variable.

I was excited to discover the [STRING_AGG](https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-2017) function.

### Approach 1
Basic join using the STRING_AGG with a GROUP BY:

```sql
-- first approach: basically works but returns duplicates names
SELECT po.PurchaseOrderID, OrderDate, PackageTypeNames=STRING_AGG(PackageTypeName, ',') 
	FROM Purchasing.PurchaseOrderLines pol 
    INNER JOIN Warehouse.PackageTypes pt ON pol.PackageTypeID=pt.PackageTypeID 
	INNER JOIN Purchasing.PurchaseOrders po ON pol.PurchaseOrderID=po.PurchaseOrderID
	GROUP BY po.PurchaseOrderID, OrderDate
```

Results of first approach:

PurchaseOrderID | OrderDate | PackageTypeNames
--- | --- | ---
1 | 2013-01-01 | Packet,Packet,Packet
2 | 2013-01-01 | Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Packet,Packet,Carton,Carton,Carton,Carton
3 | 2013-01-01 | Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each
4 | 2013-01-01 | Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each
5 | 2013-01-01 | Each,Each,Each,Each,Each,Each,Each,Each
6 | 2013-01-01 | Each,Each,Each,Each,Each
7 | 2013-01-02 | Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Carton,Each,Each,Each,Each,Each,Each,Each,Each,Each,Each
8 | 2013-01-02 | Each,Each,Each,Each

(NOTE: I'm only showing the top 8 results for all these queries, for the sake of brevity)

Close, but we have the package type name duplicated for each line item in the order.  For example, order 1 has three line items which are all type Packet.
So we need to filter that down to show only unique package types for each order.


### Approach 2
Using a subquery to select only DISTINCT package type names, then selecting from that using the STRING_AGG with a GROUP BY:

```sql
-- subquery with distinct clause
SELECT PurchaseOrderID, OrderDate, PackageTypeNames=STRING_AGG(PackageTypeName, ',') 
	FROM (
	SELECT DISTINCT po.PurchaseOrderID, OrderDate, PackageTypeName 
    FROM Purchasing.PurchaseOrderLines pol 
    INNER JOIN Warehouse.PackageTypes pt ON pol.PackageTypeID=pt.PackageTypeID 
	INNER JOIN Purchasing.PurchaseOrders po ON pol.PurchaseOrderID=po.PurchaseOrderID) d
	GROUP BY PurchaseOrderID, OrderDate
```

Results of second approach:

PurchaseOrderID | OrderDate | PackageTypeNames
--- | --- | ---
1 | 2013-01-01 | Packet
2 | 2013-01-01 | Carton,Each,Packet
3 | 2013-01-01 | Each
4 | 2013-01-01 | Each
5 | 2013-01-01 | Each
6 | 2013-01-01 | Each
7 | 2013-01-02 | Carton,Each
8 | 2013-01-02 | Each


That works.  It gives us the results we are looking for, in a relatively concise statement.  However, there is only one problem....
STRING_AGG was only introduced in SQL Server 2017, so I can't use it in my application database since we have a requirement to support 2008 and forward!

## Pre-2017 Support
Ok that works for SQL 2017, but what about prior versions?  To support prior versions of SQL Server, we can't use STRING_AGG.  A look around the web 
finds several articles which suggest to use FOR XML to generate the string.  So I decided to go with that approach.


### Approach 3 with support for pre-2017 versions of SQL Server
Here we use FOR XML to generate the string.  This joins the strings as we ask it to,
but it leaves a leading delimiter.

```sql
-- using FOR XML 
SELECT PurchaseOrderID, OrderDate, 
    PackageTypeNames=(SELECT N', ' + PackageTypeName FROM
        (SELECT DISTINCT PackageTypeName FROM Purchasing.PurchaseOrderLines pol 
        INNER JOIN Warehouse.PackageTypes pt ON pol.PackageTypeID=pt.PackageTypeID 
        WHERE pol.PurchaseOrderID=po.PurchaseOrderID) ptn
	FOR XML PATH(N'')) FROM Purchasing.PurchaseOrders po
```

Results of third approach:

PurchaseOrderID | OrderDate | PackageTypeNames
--- | --- | ---
1 | 2013-01-01 | , Packet
2 | 2013-01-01 | , Carton, Each, Packet
3 | 2013-01-01 | , Each
4 | 2013-01-01 | , Each
5 | 2013-01-01 | , Each
6 | 2013-01-01 | , Each
7 | 2013-01-02 | , Carton, Each
8 | 2013-01-02 | , Each

That is _close_, but it contains that pesky leading comma and space.

### Enter the STUFF function

The [STUFF function](https://docs.microsoft.com/en-us/sql/t-sql/functions/stuff-transact-sql?view=sql-server-2017) 
is similar to REPLACE, but it uses explicit character locations so it is more suitable
in our case since we only want to replace the leading ', ' once (rather than all occurrences).
Similarly SUBSTRING would almost fit the bill, except we'd need to know the overall length of the string,
which makes it unacceptable here.

### Approach 4 with STUFF and FOR XML
Here we add a call to the STUFF function to remove the leading ', ' from the final strings.

```sql
-- using STUFF and FOR XML 
SELECT PurchaseOrderID, OrderDate, 
    PackageTypeNames=STUFF((SELECT N', ' + PackageTypeName FROM
        (SELECT DISTINCT PackageTypeName FROM Purchasing.PurchaseOrderLines pol 
        INNER JOIN Warehouse.PackageTypes pt ON pol.PackageTypeID=pt.PackageTypeID 
        WHERE pol.PurchaseOrderID=po.PurchaseOrderID) ptn
	FOR XML PATH(N'')), 1, 2, N'') FROM Purchasing.PurchaseOrders po
```

Results of fourth approach:

PurchaseOrderID | OrderDate | PackageTypeNames
--- | --- | ---
1 | 2013-01-01 | Packet
2 | 2013-01-01 | Carton, Each, Packet
3 | 2013-01-01 | Each
4 | 2013-01-01 | Each
5 | 2013-01-01 | Each
6 | 2013-01-01 | Each
7 | 2013-01-02 | Carton, Each
8 | 2013-01-02 | Each

This yields the desired output.

## Wrap Up
In this post I described the STRING_AGG function and provided an alternative approach in order
to support older versions of SQL Server.  I focused on approaches which do not require any
temporary variables or tables so they can be used within views.

If your application needs to support versions prior to SQL Server 2017, you will likely need to use
the FOR XML or similar method to do this.  However, if you have the ability to run on 2017 or newer,
STRING_AGG is a much simpler approach.

While doing this work, I found this article by Anith Sen at Redgate to be quite helpful:
[Concatenating Row Values in Transact-SQL by Anith Sen](https://www.red-gate.com/simple-talk/sql/t-sql-programming/concatenating-row-values-in-transact-sql/)


#### References

* [STRING_AGG function](https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql)
* [FOR XML clause](https://docs.microsoft.com/en-us/sql/relational-databases/xml/for-xml-sql-server)
* [STUFF function](https://docs.microsoft.com/en-us/sql/t-sql/functions/stuff-transact-sql)
* [Concatenating Row Values in Transact-SQL by Anith Sen](https://www.red-gate.com/simple-talk/sql/t-sql-programming/concatenating-row-values-in-transact-sql/)
