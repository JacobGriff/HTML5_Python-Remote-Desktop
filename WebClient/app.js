const ws = new WebSocket("ws://localhost:8765");

var lastSend = Date.now();

function sendCommand(command, data){
    var msg = {client: "WebClient", command: command, data: data}
    ws.send(JSON.stringify(msg));
}


ws.onopen = () => {
  console.log("Connected to server");
  sendCommand("Init", "Web Client connected")
};

ws.onmessage = (event) => {

    var table = JSON.parse(event.data);
    //console.log("Message from server: ", table);

    var data = table.data;
    var command = table.command;

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
