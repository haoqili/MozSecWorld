function checkUrl(){
    var theurl = $("#inputUrl").val();
    $("#outputIframe").attr('src', theurl);
}

document.getElementById("checkButton").addEventListener('click', checkUrl, false);
