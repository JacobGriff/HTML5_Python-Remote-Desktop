const ws = new WebSocket("ws://localhost:8765");
const clientName = "WebClient"

var lastSend = Date.now();

// Get client ID from URL
var clientId = null;

function sendCommand(command, data){
    var msg = {client: clientName, command: command, data: data, target: null}
    ws.send(JSON.stringify(msg));
}

function initServer(){
    //Connect to client
}




ws.onopen = () => {
    console.log("Connected to server. Initializing.");

    const params = new URLSearchParams(window.location.search);
    clientId = params.get("id");

    console.log("Client ID: " + clientId);

    if(clientId == null || clientId == undefined || !clientId){
        console.error("Could not find client ID. Please refresh the page and try again");
        return;
    }

    initServer();
};

ws.onmessage = (event) => {

    var table = JSON.parse(event.data);


    console.log("Message from server: ", table);

    var data = table.data;
    var command = table.command;

    //Recieved data commands
    
    if(command == "Info"){
        console.log("Setting cpu to: " + data.Cpu)
        document.getElementById("Cpu-Usage").textContent = "CPU: " + data.Cpu + "%";
        document.getElementById("Ram-Usage").textContent = "RAM: " + data.Memory + "%";
    }

    else if (command === "Image") {
        // Create an image element
        const img = document.getElementById("ScreenshotImg");
        img.src = "data:image/png;base64," + data;
        img.alt = "Server Image";
        //img.width = 400; // optional

        var currentTime = Date.now();
        var diff = (currentTime - lastSend);
        
        document.getElementById("Delay").textContent = "Delay: " + diff;

        lastSend = currentTime;
    }
};


document.getElementById("getInfo").addEventListener("click", () => {
    sendCommand("Info", "None");
});

document.getElementById("getScreenshot").addEventListener("click", () => {
    sendCommand("ToggleStream", "None");
});
