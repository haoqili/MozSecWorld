$("#myform").submit(function(){
     $.post(location.href, $('#myform').serialize(), function(d) {
          $('#results').html(d);
     });
     return false; /* or else redirects */
})
