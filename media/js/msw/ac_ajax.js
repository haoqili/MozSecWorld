    function postme(){
        var theNameId = $('#theName option:selected').val();
        var theTextId = $('#theText option:selected').val();

        url = "ac_ajax_server";
        //url = $('form').attr('data-url'); // issue #59
        //alert(url);

        var csrfvalue = $('input[name=csrfmiddlewaretoken]').val();

        var sendData = {
            inpNameId: theNameId,
            inpTextId: theTextId,
            csrfmiddlewaretoken: csrfvalue
        };

        $.post(url, sendData,
            function(data) {
                $('#output').html(data);
            }
        );

    }

    
    document.getElementById("memPostButton").addEventListener('click', postme, false);
   
