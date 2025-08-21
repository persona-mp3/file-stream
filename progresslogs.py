WELL, the progress made so far is really interesting, after a couple weeks, reading TCP Documentations, learning socket programming and how UNIX && Python handles it,
I've been able to create one similiar to the one I wanted and successfully shot myself in the foot. 
The main problem with the previous one is with the Client Architecture. I did not put into consideration about how it will tell send multiple files in a session 
instead of each file is it's own client, and also integrating it with Go.

While this clearly calls for a rewrite, or even a throwaway of the first one, the issue is grandiose, easy to solve, quite complex to tell the computer what to do.
Handling the protocol of something like this will be a journey, but won't kill us, so here are the things I think should be focused on, during this new version.
We'll just call it version 1.0

1. We need to make request headers for verification of each packet operation. For example if the packet with a tag of 12, we found out something went wrong, 
   We inform the client, and they send it again, depending on what the situation might be. And also communicate for every request, there must be a response.

2. We also need to get more familiar with Python's OS-Module on IO operations, as it seems things here are really as straight forward as the language.;

3. We also need to make sure that the CLIENT can send multiple files at once, instead of making each file a seperate client on the server. We should also include multithreading 
   on both client and server to handle concurrency as file IO in python are blocking, so are all socket operations.

=========================================
      REQUEST-RESPONSE
=========================================
So starting with the Client, we need to make sure that 
1. We dont send any other packet unless we've recieved reponse from the server that the last packet was successful. 
   To make it easy, we can make it text-based, instead of bytes, to avoid much decoding as no data is sent, similar to the ACK-STAGE


We need to include versioning inside this new protocol, so new req-response will be like this: 
  Content-Length: 128
  Version: 001
  Request-Type: Packet
  Sent: 12
  Tag: 12
  Author: file_name
  Data: "New Protocl Version"

13:07 July 21st
2. Second Problem is this, for every packet that the client sends, we are opening that same file again, which I assume, can cause
   a huge amount of overhead, and also, theres no indication telling the server on the client, 
   "Hey Server, I'm done, I want to close the connection"
   And the file we keep opening, does not even close.
   So if we can use a threadpool?? Such that for each file that is being sent by the client, we can assign a seperate thread to it 
   that always has its own particular file open, and when the Client wants to close or is done with the file, we can just close the file then. 
   We also need to incorporate flags into the protocol, if this file we are sending is in a sub-directory and include it in. 
   We should just make this a new version at this point, we'll use version1. 
   And by the time all threads are closed, we can assume the client is Done.
   

==========================================================================
      Monday: 09:27 July 28th 
==========================================================================
So I'm trying to think here in terms of multithreading. And these are the following thought patterns I can seem to figure out now at the moment:
  i. When the client sends a list of the files the are about to send, we using multithreading to first create these folders and sub-directories.
     This is during the Ack-Stage of the protocol. 

  ii. And then we can also use multithreading on the client side to stream these files too?? Seems logical and possible, that means the server will 
      also have to write the content using threads too. So for each file, we assign them a thread on the server, and on the client?? 

  iii. We can just make each file a thread, and new request to the server. And then let the server handle it.

  So during the Ack-Stage, we send a list of files and all sub-files we need to send to the server, and then server creates their directories as placeholders
  When the client recieves and Ack-Response, we can now stream each file in a thread, by making a new Request, saying "This is another file, here are the contents"
  And then signal the close of the thread. But, there is a caveat to this. Theres only a limited amount of threads a computer can have w/o collapsing. 
  And I'm def not allowing Jeff Bezos to tax me. Well, we can also put a cap to how much we can thread at once. Yea ts getting more complex

  - Questions:
  1. Do we need to keep track of which file has been streamed and successful, I mean, the threads could just end themseleves and that's it, what about failures?
     If something didn't succeed, how should it be propagated, because each file from a client all share the same port? 


==========================================================================
   Tuesday:  11:33 July 29th
==========================================================================
Due to extreme pondering, I decided that while the multithreading-concept or remote-multithreading is cool, it's overengineering, and overkill for 2 users. Theres at lease 500 
network ports open for 3users, and it's really a bad idea to send remote execution if im being honest. But I've been able to make progress.

  PROGRESS REPORT:
  - Nested files and directories can now be written to successfully, although it has not been integrated with the the project yet, it's done. 
      The pathlib library was mostly used to do this, as I'd probably be switching most IO operations to start using Path mainly on the server but should be compatible otherwise.
      Path also handles automatic closing but hopefully it does throw tantrums when it's time to stream. 

  REMAINING WORK:
  - We also need to be able to decided when to end the session for the file to be fairs

  POSSIBLE FEATURES:
  - To avoid overloading server, we can make a queue for the files, we can stream 8 at once, and then so on.
  - Also I don't know if I should allow other file formats like png, jpg and others, as the server just goes offline if it expects something else




==========================================================================
  Thursday:  19:02 Auguust 07th
==========================================================================
Implemented the following features:
  Error-Reponse to be used when an internal error occured 
  Malformed-Packet response to be used when an invalid reponse/packet has been sent by client/server alike 
  Packet-Status  for each packet 
  Unit and regression testing for each modules
  Refactored server_v1.py and client_v1.py has the above new features implemented




==========================================================================
    Friday: 13:00:59 Auguust 08th
==========================================================================
We need to add a retry logic, this will need essential testing

So the server needs to track each packet it receives and compare each one.
PSEUDOCODE looks something like this -> 
  previous_packet_id = 12
  expected_packet_id = 13
  new_packet = recv_packet()

  if previous_packet_id != expected_packet_id {do something}

  // if we wanted to retry, we could change the packet-status code to be 300
  Request-Type:  Packet-Status
  Status-Code: 300
  Packet-Id: 12
  Expected-Packet: 12
  Recvd-Packets: 12

  The Packet-Id , Expected-Packet are the same because we want to infer that message to the client and to avoid confusion 
  when trying to debug the protocol. And the Recvd-Packets represents the number of packets the client server has recvd

  But for some reasons, will there be packets where they were unsucessfull and ask for a retry?
  But we could mock them just to see

  
