
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

const clientName = "WebClient";

var lastSend = Date.now();

var initialized = false;

function openClient(id){
    window.open("Client/index.html?id=" + id, "_self");
}

function initServer(){
    var msg = {client: clientName, command: "Init", data: null};
    ws.send(JSON.stringify(msg));
}

function getClients(){
    var msg = {client: clientName, command: "GetClients", data: null, target: null}
    ws.send(JSON.stringify(msg));
}

function displayClients(clients){
    console.log("Do something here");

    var clientCount = clients.length;
    if(clientCount > 0){

        clients.forEach(client => {

            var table = client;
            console.log(table);
            console.log("Creating new client div");

            var clientHolder = document.getElementById("clientHolder");
            var prefabClient = document.getElementById("prefabClient");
            var newClient = prefabClient.cloneNode(true);
            clientHolder.appendChild(newClient);

            //Set vars
            var id = table.Id;
            var info = table.Info;
            var resources = table.Resources;
            var screenshot = JSON.parse(table.Screenshot);
            
            var newClient_id = newClient.querySelector(".clientId");
            newClient.id = id;
            newClient_id.textContent = id;

            console.log("ID: " + id);

            var newClient_info = newClient.querySelector(".clientInfo");
            newClient_info.textContent = info;

            var newClient_resources = newClient.querySelector(".clientResources");

            console.log(resources);
            console.log(resources.CPU);

            newClient_resources.textContent = ("CPU: " + resources.Cpu + "% | RAM: " + resources.Memory + "%");

            if(screenshot != null){
                var newClient_screenshot = newClient.querySelector(".clientScreenshot");
                newClient_screenshot.src = "data:image/png;base64," + screenshot;
            }

            var clientOpenButton = newClient.querySelector(".clientOpen");
            clientOpenButton.onclick = function() {openClient(id); };

            console.log("Set onclick to " + id);
        });
        
    } else{

    }
}

function pickClient(){

}


function onConnection(){
    console.log("Connected to server. Initializing.");
    initServer();
}

function onMessage(event){
    var table = JSON.parse(event.data);
    console.log("Message from server: ", table);

    var data = table.data;
    var command = table.command;

    //Setup commands
    if(command == "Init"){
        initialized = data;
        console.log("Initialized: " + initialized);
        if(initialized){
            getClients();
        } else{
            console.error("Initialization failed...");
        }
    } else if(command == "GetClients"){
        displayClients(data);
    }
}