# HTML5_Python-Remote-Desktop

### This is a project to allow you to setup a remote client, server, and web portal to be able to access any device remotely over your local network. This was created to achieve remote access without using any external servers, and allowing full customization of usability and bandwidth.

# Features:
  - [ ] Support for multiple clients & web portal instances: X
  - [X] Single Client and Web Portal Usability: O
  - [X] Real-Time Screen sharing: O Speed: 20FPS / 50ms Delay
  - [ ] Device Hardware Information: (May add more as time goes on)
    - [X] CPU & Ram Usage: O
    - [ ] System name, Main drive storage: X
  - [ ] File Viewer: X
    - [ ] Drives & Storage: X
    - [ ] File Browser: X
    - [ ] Image/Audio Viewer: X
    - [ ] File Download: X
    
  - [ ] Command Line: X

# Specs:

### Python Server: The brains of the operation. Handles all communication between the Web Clients and the Remote (Python) Clients
  Protocol: WebSockets
  
  1. Stores client data in classes for remote desktop clients and web clients:
     * Remote Desktop Client (Python Client to get data from Stores info to send to the web clients on request, and filters out duplicates to save bandwidth. This means that when a new web client connects, it can request to get the latest information from any or all remote desktop clients):
       * ClientID
       * WebSocket (Saved socket connection so we can access it using its ID. We may use a map that stores IDs/Names along with the client class so its more efficient than looping through all classes. I should do a test on this actual speed in Python.)
       *  Device Info (Device name, Resource usage, Main Drive Storage, etc)
       *  Latest Screenshot
       *  All Toggles (This gets sent to the web client to visually update toggle buttons so you know if its sending realtime updates on specific things like screen sharing!)
     * Web Client (HTML5/JS Client that requests data from Remote Desktop Clients):
       * ClientID (Potentially target, depends how its programmed for which client you're viewing. I may just do it based on web url...)
       * WebSocket
       * ConnectedID (The ID of the desktop client so we can loop through all web clients and send data to any connected to this specific client)
       * Potentially more data as this gets more complicated
      
  2. Listens to command requests from web clients and forwards request to relevant remote desktop client
  3. Recieves data from remote desktop client in two ways: One off Requests, repeating frame chunks:
     * One off requests: Requests such as getting client info, it sends this data one time to the server. Also for toggles, it'll change the toggle variable in the client class on the server and on the clients running python script
     * Repeating frame chunks: Every frame the client will go through all its toggles and send all toggled data to the server. This is faster than having the server holding the data, plus makes it easier for multiple python clients
     * It may be more efficient if we make all of this one big chunk of data being sent, instead of sending multiple data streams?
     * We could also not send data if it is a repeat to save bandwidth. For example in screenshare if nothing changes, it'd save a large amount of data (assuming that's possible with image compression? Using pyautogui images, may also be faster method)
  5. Sends data back to web clients:
     * Whenever the client updates the server, it will send the update to all connected web clients

### HTML5/JavaScript Web Portal

Uses WebSockets to communicate with the server:
  * Home page showing all python-clients & basic client info
  * Client Viewing Page
  * Sends requests to the server for a specific client:
    * Data includes Sender source (Web client), Target (Specific Python Client), Command (Request such as device info, or toggle such as screen share), and any arguments (Additional parameters such as file address to download. Can be null for basic commands like device info, or toggles)
    * Can optimize by not including target but instead sending information once on the first connection to the client when you visit its portal page
  * Sends global requests for all clients:
      * Home page viewing, same command structure, target can be null to get all clients to send info, then the page renders the info based on lowest to highest ID or if we incorporate sorting
  * Could incorporate a timeout system and send anti-timeout messages periodically, otherwise we just make sure socket connection exists and if it doesnt remove from map of web clients 
    
### Python-Based Client:
Stores which toggles are enabled and sends data at a fixed rate to the server

# Extra

- [ ] Encryption

## Customizability: At the moment you can only toggle on/off monitoring features, so you can only use whatever bandwidth you like. I may or may not add more customizability to this, depending how far I want to work on this project.
  - [ ] Frame rate for clients to send data
  - [ ] Disable all client data sending when no one is viewing clients
  - [ ] Customize Web portal Home page and options
  - [ ] Customize Web portal layout (This will likely be last to add)
  - [ ] Remote Desktop client ordering / IDs / Names
