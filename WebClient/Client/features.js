var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
var container = document.getElementById("ScreenshotImgContainer");
output.innerHTML = slider.value;

slider.oninput = function() {
    var size = this.value;
    output.innerHTML = size;
    container.style.width = size + "vw";
    container.style.height = size + "vh";
}