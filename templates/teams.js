$(document).ready(function() {
    $('#assign_cards').click(function(){
       var element = document.getElementById("PlayerID");
       //var tarURL = "{{ url_for ('get_driver') }}?id=" + element.value;
       console.log(tarURL);
       $.ajax({
        url: tarURL,
        type: "GET",
        success: function(response) {
            //$("#myimg").attr('src', '/static/' + response);
       },
       error: function(xhr) {
         //Do Something to handle error
      }
      });
    });
 });

 $(document).ready(function() {
   $('#assign_driver').click(function(){
      var element = document.getElementById("DriveID");
      //var tarURL = "{{ url_for ('get_driver') }}?id=" + element.value;
      console.log(tarURL);
      $.ajax({
       url: tarURL,
       type: "GET",
       success: function(response) {
           //$("#myimg").attr('src', '/static/' + response);
      },
      error: function(xhr) {
        //Do Something to handle error
     }
     });
   });
});