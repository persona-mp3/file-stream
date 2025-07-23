### The Protocol Structure

To start a session with the server, an Ack-Request needs to be sent. Anything other than that will be rejected, as the server will not respond.
An Ack-Request is mainly for the following reasons:

1. To see if the server is active 
2. To tell the server the amount of data to expect 
3. Where we are currently connecting from in the operating system ie Current Working Directory, CWD


### FIRST STEP: ACK-REQUEST-RESPONSE
The expected response from the sever is an ```Ack-Response```. This two-way comnunication is done using text like how HTTP works. The ```Ack-Request```
has the following structure:
```ts
    Request-Type: Acknowledege \r\n
    N-Packets: 234 \r\n
    CWD: rengoku \r\n
    Author: protocol.md \r\n
```

```N-PACKETS``` will be explained later below. The simply tell the serve: "Hey Im sending N_PACKET heads-up"


The ```Author``` in this case is the file the server should expect. The server will then do this:
    - Create a directory to store this file and other subsequent files after, gotten from the CWD field
    - Create the first file
    - And the send the ```Ack-Response``` to the client, in the following structure, which again is text-based:

```ts
    Request-Type: Acknowledege \r\n
    Status: Acknowledeged \r\n
```

Any other reasons, the server might send a ```Status``` rather than ```Acknowledged``` have not been decided yet, but would be mainly due
to authentication issues, but should be handled by a proxy-server instead.


After the client has verified the ```Ack-Response``` from the server, then we can now begin to exchange data packets

### SECOND STEP: DATA PACKETS
How the client and serve share files is quite simple and straightfoward. The client reads the whole file into chunks, and then sends each one to the server.
The ```Packet-Request``` has the following fields/structure:

```ts 
    Request-Type: Data-Packet
    Content-Length: 30
    Sent: 1
    Tag: 0 
    Data: "print("hello world)"
```
All communications during this exchange is mainly BYTES, and I will explain the structure. However, there are simple pre-requisites for you know:

1. Endianess -> BigEndian and LittleEndian
2. Pythons  ```struct``` module
3. Able to understand array slicing and using offsets


===============================================================

This is how the client prepares the file and sends it over to the client:
1. Reads the file in chunks and stores them
```py 

file = open(file_name, "rb") # opening the file to read-bytes, wrap this in a try-except 
file_content = []
while True:
    content = file.read(1024) # reading contents of file every 1024 bytes
    if content == b'':
        print("EOF")
        break
    file_content.append(content)
```
2. Now to tell the server how many packets to expect for this packet, we just get the lengt of the ```file_content``` list
3. We then send each of these contents in chunks to the server to process, using a ```while loop```,lol.

This is the packet structure for what we are sending to the server:
```py
packet = content_len + req_type + sent + tag + data
```
However it is more complex than that as we have to also add the length of each field to know how to decode this on the sever to it will look like this:
```py
packet = content_len + req_type_len  + req_type + sent_len + sent + tag_len + tag + data
```
All these are in bytes it the ```utf-8``` format. But here is where the details are:

For each packet we send, we need to label it with a ```Tag``` so the server can keep in sync, or incase an error occured in any IO operation, the sever can tell us 
which packet it had a problem with simply by refrencing the ```Tag``` number. Think of it like each's packet ID number. This tag derived from the number of packets gotten 
previously from:

```py 
N_PACKETS = len(file_content)
tag = 0
packet_sync = 0
sent_packets = 1
while packet_sync < N_PACKETS:
    data_to_send = file_content[packet_sync]
    # organise packet-structure here
    tag += 1
    sent += 1
    packet_sync += 1
```
At this point, if it still makes 0 sense, that's how it was for me trying to get the bare-bones, just let me know so you won't go bald.

And for every data packet that has been fully made, we need to get the content length of the whole packet we are sending to the server. You can 
alias ```content_length``` as ```packet-size```, or ```header```. ```header``` is mostly used on the client-side and ```content_length``` is used on the server-code.

For this explanation, we will use ```packet-size``` from now on.
So we need to get the let the sever to know the size of this packet. and we can get this by simply getting the length of the total data organised together:
```py 
packet = content_len + req_type_len  + req_type + sent_len + sent + tag_len + tag + data
packet_size = len(packet)
```

BUTTT, not yet done, we need to also encode this ```packet_size``` in bytes, and we need to use 4-Bytes. Why? 4bytes, can hold numbers up to ```2**32 ```, because depending 
on how big the file might be, we just need to make sure we can accomodate that number, anything other than that, we rejecting it. We are also doing this for the ```Tag``` and ```Sent```
fields. The ```Sent``` field just tells the server the number of packets we have sent so far. And because of ```Endianess``` we need to use ```BigEndian``` to encode this. This will 
always look this:
```py 
# ENCODING in BigEndian
# struct.pack(format: str, v1: int) -> bytes
header = struct.pack("!I", packet_size)
sent_len = struct.packet("!I", len(str(sent)))

# DECODING 
# we read the first 4bytes from the packet
content_length = packet_from_client[:4]

# and then decode in BIGENDIAN! Otherwise, python will raise an annoying Exception
# struct.unpack(fmt: str, v1: int) -> tuple(value: int, ...)
decoded_content_length = struct.unpack("!I", content_length)[0]
```

This decoding will be done until we reach the data and you can find how it is mainly done in [decode_packet.py](./encoders/decode_packet.py).

Other instances of decoding on the server is done at [server.py](./server.py#143). It gets tuff and induces balding changing anything if you aren't 
familiar with array or string slicing.

Encoding is done in [client.py](./client.py#75). You'll see how every it is bundled together and then sent to the TCP Server
