### New Changes
Although, the previous concepts of the first Version are still intact, this second version is more precise and robust. 
It includes data checksums for packet-integrity, structure logging and concurrency on both client and server. 


## Structure
For all Request and Responses sent, they must contain the Version that they want to use. Currently, the only supported 
version is ```Version 2```. Here's the general structure for all Responses and Requests:


    ```
    Version: 002 \r\n
    Request-Type: Acknowledge \r\n
    Expected-Packets: 12 \r\n
    CWD: wsl-prt \r\n
    Author: protocol-v2.md
    ```

The above is the  ```Ack-Request``` which is the first Request that must be sent by the client. And the server must also send an ```Ack-Response```. The only time the server does not respond to an ```Ack-Request``` is when the client sends a payload of size above ```2^10``` which is too much data for us to handle.

One final thing to note about the ```Ack-Request-Response``` is that it's text-based, like HTTP as it is denoted by carraige returns. 

The ```Ack-Response``` is crucial to the client especially as it contains a session id that helps the client to verify themselves if they want to resume 
a session. The session id is generated using the ```uuid``` module in python. When this is receieved by the client, they are to save it in a ```ssid``` file.


### Other Supported Requests
1. ## Packet-Request
    This protocol among others are binary encoded. For each field encoded, it has it's pre-pended field length encoded. For example:

    ```
    [4B content-length]
    [1B version-length][version] 
    [1B request-type-length][request-type]
    [1B sent-packets-length][sent-packets]
    [1B packet-tag-length][packet-tag]
    [1B checksum-length][sha256 hash]
    [data]
    ```
The ```Content-Length``` field is used to denote the whole size of the packet, to let the receiver know how much bytes to read to get a whole packet. 
The ```Packet-Request``` finally looks like this:
    
    ```
    Content-Length: 1900 
    Version-length: 3 
    Version: 002 
    
    Request-Type-Length: 20 
    Request-Type: Packet-Request 
    Sent-Packets-Length: 3 
    Packet-Tag-Length: 5 
    Packet-Tag: 320
    Checksum-length: 46
    Checksum: 0akeu7lefkn37ajeugb12uks 
    data: Hello World
    ```
    

The ```Content-Length``` is encoded using Network Order, Big-Endian. 4bytes was chosen so a huge amount of data could be represented. 
All other length fields are encoded in a single-byte which can represent from 0-255 bits


2. ## Disconnect-Request 
    Used to inform the server that we are done with all sending all files and they can close to connection.


    ```
    Content-Length: 90
    Version-length: 3 
    Version: 002 
    
    Request-Type-Length: 20 
    Request-Type: Disconnect
    Request-Code: 000
    ```


3. ## Packet-Status Response
    Used to inform the client on every packet receieved, whether successful or failed.
    The ```Packet-Status``` Response could also tell the client to resend a packet. 
    A ```Status-Code``` of ```200``` means the client can send the next packet, and ```201``` means ```Retry```. 
    And instead of ```Packet-Status``` it will be a ```Retrial``` in the response to the client.


    ```
    Content-Length: 1900 
    Version-length: 3 
    Version: 002 
    Request-Type-Length: 12 
    Request-Type: Packet-Status

    Status-Code-Length: 3
    Status-Code: 200 
    Packet-Tag-Length: 5
    Packet-Tag: 320

    Received-Packets-Length: 3
    Received-Packets: 3

    Expected-Packet-Length: 6
    Expected-Packet: 6

    ```
    

All other responses from the server follow the same structure:


    ```
    [4B content-length]
    [1B version-length][version] 
    [1B request-type-length][request-type]
    [1B status-code-length][status-code]
    ```

4. ## Ack-Response:

    ```
    Content-Length: 800
    Version: 002 \r\n
    Request-Type: Acknowledged \r\n
    SessionId: protocol-v2.md
    ```
## Others:
5. Operational Response
6. Corrupted Response
7. Unsupported Response
8. Malformed Response
