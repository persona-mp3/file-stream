How are we going to do retrials? 

First, we can assign on Ack-Response, a sessionId

But what situations do we need retrials, as we'll need a place to store these information 
We can use REDIS
Why?
    Redis is extremely lightweight and fast
    Compared to others NOSQL, we just need to store sessionId along with their operation status mapped to key-value
    We mainly need fast caching and index-look ups too

Although, i'm not sure about how well it integrates with Python, or if we'd need a server runnigng to keep it alive.


So when a client reconnects, they provide us with a sessionId, packet-id on where we last stopped, 
all other data can be retrieved from the Redis database. 

So what if a packet is changed before another connection, well since each packet has a checksum for the data it's carrying, 
if the data differs the slightest for that file, we create a new one, 
Or during the ack requst for each file, we send the checksum for server to verify after

    =========================================
        Ack-Request for main.go
        Request-Type: Acknowledge \r\n
        Author: main.go \r\n
        N_Packets: 30 \r\n
        FileCksum: jd348239842398yewb3224y \r\n
    =========================================

So by the time the server is done reciving all the packets for main.go , it will run a checksum for it and hopefully, 
if they match, we'll go on.

But this does not answer the question that was posed earlier. Now since we know the cksum of this entire file, we'll
also have the cksum of each packet, we'll we will also need to store the file-cksum too, in memory or maybe a file, thats why redis 
also works but the data structure is getting a bit more convoluted. 
But yes, we'd store the file-checksum in memory explicitly, and the only time we'll store a a packet-cksum if there was a  
prior disaster

So when a client connects again, with a Retiral request, they include their sesssion Id, fileCkSum, packetId, packetCksum, 

====================================================
        Request-Type: Retrail \r\n 
        SessionId: kj84038i2334234 \r\n
        Author: main.go \r\n
        FileCksum: 123479x32 \r\n
        PacketId: 12 \r\n
        DataCksum: 000005x6 \r\n
====================================================

Now the server, will parse this request and check Redis, 
GET kj84038i2334234
And we should expect the following data model:

===========================================
        kj84038i2334234: {
            reason: error,
            author: main.go,
            lastPacketId: 12,
            fileCksum: 123479x32,
            dataCkSum: 000005x6,
        }
===========================================
If for any reason, the sessionId does not exist, we fail the retrial request, meanining they need to start a New-Ack
If the author does not match, we tell them to make a New-Ack

But if the Author and SessionId exists:
    If the lastPacketId differs, new Ack.
    If fileCksum differs, new Ack 
    if dataCksum differs, new Ack 

Else, we contiue from the 12th one

ANOTHER ISSUE>
how does the client know where they stopped -> we could just make a .renof file to store basically the same data
what if we can't get the logs?
