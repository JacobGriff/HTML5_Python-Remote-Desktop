const ws = new WebSocket("ws://localhost:8765");
const clientName = "WebClient"

var lastSend = Date.now();

var initialized = false;

function openClient(id){
    window.open("Client/index.html?id=" + id, "_self");
}

function initServer(){
    var msg = {client: clientName, command: "Init", data: null, target: null}
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
            console.log("Creating new client div");

            var clientHolder = document.getElementById("clientHolder");
            var prefabClient = document.getElementById("prefabClient");
            var newClient = prefabClient.cloneNode(true);
            clientHolder.appendChild(newClient);

            //Set vars
            var id = table.Id;
            var info = table.Info;
            var screenshot = JSON.parse(table.Screenshot);
            
            var newClient_id = newClient.querySelector(".clientId");
            newClient.id = id;
            newClient_id.textContent = id;

            var newClient_info = newClient.querySelector(".clientInfo");
            newClient_info.textContent = info;

            if(screenshot != null){
                var newClient_screenshot = newClient.querySelector(".clientScreenshot");
                newClient_screenshot.src = "data:image/png;base64," + screenshot;
            }
        });
        
    } else{

    }
}

function pickClient(){

}


ws.onopen = () => {
  console.log("Connected to server. Initializing.");
  initServer();
};

ws.onmessage = (event) => {

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
};