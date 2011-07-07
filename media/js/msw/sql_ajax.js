    function check(){
        var inputSql = $("#inputSql").val();
        //alert(inputSql);

        var url = "sql_ajax_server";
        //alert(url);

        var csrfvalue = $('input[name=csrfmiddlewaretoken]').val();
        //alert(csrfvalue);

        var sendData = {comment: inputSql, csrfmiddlewaretoken: csrfvalue};

        $.post(url, sendData,
            function(data) {
                //data modifications:
                data = data.replace(/],/g, "<br />");
                data = data.replace(/\[/g, "");
                data = data.replace(/]]/g, "");
                // Dump 
                $('#output').html(data);

                /*
                // Prettier display CANNOT work because each char is an elet in array
                // Clear current data
                $('#output').html("");
                alert(jsonData);
                var data = $.parseJSON(jsonData); 
                alert(data);
                for (i=0; i<=5; i++){
                    $('#output').append(data[i]);
                }
                */
            }
        );

    }

    
    document.getElementById("checkButton").addEventListener('click', check, false);
   
