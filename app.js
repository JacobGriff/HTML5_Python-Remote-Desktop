//Attempt to get web socket
var ws = null;

async function getWebSocket(){
    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = onConnection;
    ws.onmessage = onMessage;

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
        console.log("Connection closed, retrying...");
        setTimeout(getWebSocket, 2000); // retry after 2s
    };
}

window.onload = function(){
    console.log("Connecting to web socket");
    getWebSocket();
}


const clientName = "WebClient"

var lastSend = Date.now();

// Get client ID from URL
var pythonClientId = null;

function sendCommand(command, data){
    var msg = {client: clientName, command: command, data: data}
    ws.send(JSON.stringify(msg));
}

function initServer(){
    //Connect to client
    sendCommand("Init", pythonClientId);
}

function onConnection() {
    console.log("Connected to server. Initializing.");

    const params = new URLSearchParams(window.location.search);
    pythonClientId = params.get("id");

    console.log("Client ID: " + pythonClientId);

    if(pythonClientId == null || pythonClientId == undefined || !pythonClientId){
        console.error("Could not find client ID. Please refresh the page and try again");
        return;
    }

    initServer();
};

function onMessage(event) {

    var table = JSON.parse(event.data);


    console.log("Message from server: ", table);

    var data = table.data;
    var command = table.command;

    //Recieved data commands

    if(command == "Init"){
        //Initialized, now request cached data back on success
        if(data == true){
            console.log("Initialized Successfully. Polling cached data");
            sendCommand("PullSaved", null);
        } else{
            console.error("Warning, initialization failed.");
        }
    } else if(command == "PullSaved"){
        //Recieved all data, now update everything
        updateAll(data);
    }
    
    else if(command == "Resources"){
        updateResources(data);
    }

    else if (command === "Screenshot") {
        updateLiveStream(data);
    }

    else if(command == "GetFiles"){
        updateFiles(data);
    }

    else if(command == "GetDrives"){
        updateRootDrives(data);
    }


    else if(command == "PermissionError"){
        alert("Permission Error: " + data);
    }
};


//Updater functions
function updateAll(data){
    console.log("Updating all data: ", data);
    var resources = data.resources;
    var screenshot = JSON.parse(data.screenshot);
    var rootDrives = data.rootDrives;

    updateResources(resources);
    updateLiveStream(screenshot);
    updateRootDrives(rootDrives);

    //var files = {"Dir": "C:\\", "Files": rootDrives["C:\\"]["Files"]}
    //updateFiles(files)
}

function updateRootDrives(rootDrives){

    console.log(rootDrives);

    var currentDirectoryEl = document.getElementById("CurrentDirectory");
    currentDirectoryEl.textContent = "~Root";

    const container = document.getElementById("fileViewerContainer");

    //Clear
    container.innerHTML = "";

    const namePreset = document.getElementById("drivePresetName");
    const storagePreset = document.getElementById("drivePresetStorage");
    const openPreset = document.getElementById("drivePresetOpen");

    for(const key in rootDrives){
        const drive = rootDrives[key];
        const freeSpace = drive.Free;
        const totalSpace = drive.Total;

        const spaceText = freeSpace + "/" + totalSpace;

        //Create new entry

        var nameEl = namePreset.cloneNode()
        var storageEl = storagePreset.cloneNode();
        var openEl = openPreset.cloneNode(true);

        nameEl.textContent = key;
        storageEl.textContent = spaceText;

        openEl.querySelector("button").onclick = function(){
            console.log("Clicked open button. Opening Drive: " + key)
            sendCommand("GetFiles", key);
        }

        container.appendChild(nameEl);
        container.appendChild(storageEl);
        container.appendChild(openEl);
        
    }
}

function updateFiles(Folder){

    console.log("Updating files: ", Folder);

    const container = document.getElementById("fileViewerContainer");

    //Clear
    container.innerHTML = "";

    const currentDirectoryEl = document.getElementById("CurrentDirectory");

    const namePreset = document.getElementById("fileViewerPresetName");
    const sizePreset = document.getElementById("fileViewerPresetSize");
    const openPreset = document.getElementById("fileViewerPresetOpen");
    const downloadPreset = document.getElementById("fileViewerPresetDownload");

    const Directory = Folder["Dir"];
    const Files = Folder["Files"];

    currentDirectoryEl.textContent = Directory;

    console.log("Files:", Files)

    for(const file in Files){
        //Create new entry
        
        var nameEl = namePreset.cloneNode()
        var sizeEl = sizePreset.cloneNode();
        var openEl = openPreset.cloneNode(true);
        var downloadEl = downloadPreset.cloneNode(true);

        var sizeText = Files[file] ? Files[file] : "Folder";

        nameEl.textContent = file;
        sizeEl.textContent = sizeText;

        if (sizeText == "Folder"){
            openEl.querySelector("button").onclick = function(){
                var folderLocation = Directory + "\\" + file
                console.log("Opening Location: " + folderLocation)
                sendCommand("GetFiles", folderLocation);
            }
        } else{
            openEl.querySelector("button").onclick = function(){
                alert("Cannot open files yet");
            }
        }

        downloadEl.querySelector("button").onclick = function(){
            alert("Cannot download files or folders yet");
        }

        container.appendChild(nameEl);
        container.appendChild(sizeEl);
        container.appendChild(openEl);
        container.appendChild(downloadEl);
    }
}

function fileDirectoryBack(){
    //Get current directory and ask to get one before it
    const currentDir = document.getElementById("CurrentDirectory").textContent;

    console.log("Go back a directory from: "+ currentDir)
    sendCommand("BackDirectory", currentDir);
}

function updateResources(resources){
        document.getElementById("Cpu-Usage").textContent = "CPU: " + resources.Cpu + "%";
        document.getElementById("Ram-Usage").textContent = "RAM: " + resources.Memory + "%";
}

function updateLiveStream(screenshot){

        //Update image
        const img = document.getElementById("ScreenshotImg");
        img.src = "data:image/png;base64," + screenshot;
        img.alt = "Server Image";

        //Get delay to show fps!
        var currentTime = Date.now();
        var diff = (currentTime - lastSend);
        
        document.getElementById("Delay").textContent = "Delay: " + diff;

        lastSend = currentTime;
}

//Listeners

document.getElementById("getResources").addEventListener("click", () => {
    sendCommand("Resources", "None");
});

document.getElementById("getScreenshot").addEventListener("click", () => {
    sendCommand("ToggleStream", "None");
});

document.getElementById("FileBackButton").addEventListener("click", () => {
    fileDirectoryBack();
});
