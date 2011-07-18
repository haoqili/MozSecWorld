    function check(){
        var inputSql = $("#inputSql").val();

        var url = "sql_ajax_server";

        var csrfvalue = $('input[name=csrfmiddlewaretoken]').val();

        var sendData = {comment: inputSql, csrfmiddlewaretoken: csrfvalue};

        $.post(url, sendData,
            function(data) {
                //data modifications:
                data = data.replace(/],/g, "<br />");
                data = data.replace(/\[/g, "");
                data = data.replace(/]]/g, "");
                // Dump 
                $('#output').html(data);
            }
        );

    }

    
    document.getElementById("checkButton").addEventListener('click', check, false);
   
