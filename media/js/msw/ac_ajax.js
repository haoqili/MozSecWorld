    function postme(){
        var theName = $('#theName option:selected').text();
        alert(theName);
        var theText = $('#theText option:selected').text();
        alert(theText);

        url = "ac_ajax_server";

        var csrfvalue = $('input[name=csrfmiddlewaretoken]').val();

        var sendData = {
            inpName: theName,
            inpText: theText,
            csrfmiddlewaretoken: csrfvalue
        };

        $.post(url, sendData,
            function(data) {
                $('#output').html(data);
            }
        );

    }

    
    document.getElementById("memPostButton").addEventListener('click', postme, false);
   
