# HTML5_Python-Remote-Desktop

This is a project to allow you to setup a remote client, server, and web portal to be able to access any device remotely over your local network. This was created to achieve remote access without using any external servers, and allowing full customization of usability and bandwidth.

Features:
  Support for multiple clients & web portal instances: X
  Single Client and Web Portal Usability: O
  Real-Time Screen sharing: O Speed: 20FPS / 50ms Delay
  Device Hardware Information: (May add more as time goes on)
    CPU & Ram Usage: O
    System name, Main drive storage: X
  File Viewer: X
    Drives & Storage: X
    File Browser: X
    Image/Audio Viewer: X
    File Download: X
    
  Command Line: X

Specs:

Python Server: The brains of the operation. Handles all communication between the Web Clients and the Remote (Python) Clients
  Protocol: WebSockets
  Listens to command requests from web clients,

HTML5/JavaScript Web Portal:
    Uses WebSockets to communicate with the server
    Home page showing all python-clients & basic client info: X
    Client Viewing Page: O
    Sends requests to the server for a specific client:
      Data includes Sender source (Web client), Target (Specific Python Client), Command (Request such as device info, or toggle such as screen share), and any arguments (Additional parameters such as file address to download. Can be null for basic commands like device info, or toggles)
      Can optimize by not including target but instead sending information once on the first connection to the client when you visit its portal page
    Sends global requests for all clients:
      Home page viewing, same command structure, target can be null to get all clients to send info, then the page renders the info based on lowest to highest ID or if we incorporate sorting
    
Python-Based Client:
  Stores which toggles are enabled and sends data at a fixed rate to the server
  

  Encryption: X

  Customizability: At the moment you can only toggle on/off monitoring features, so you can only use whatever bandwidth you like. I may or may not add more customizability to this, depending how far I want to work on this project.
  To add: 
    Disable all client data sending when no one is viewing clients
    Customize Web portal Home page and options
    Customize Web portal layout (This will likely be last to add)
    Remote Desktop client ordering / IDs / Names
