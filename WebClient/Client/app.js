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
};


//Updater functions
function updateAll(data){
    var resources = data.resources;
    var screenshot = data.screenshot;

    updateResources(resources);
    updateLiveStream(screenshot);
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

document.getElementById("getInfo").addEventListener("click", () => {
    sendCommand("Resources", "None");
});

document.getElementById("getScreenshot").addEventListener("click", () => {
    sendCommand("ToggleStream", "None");
});
