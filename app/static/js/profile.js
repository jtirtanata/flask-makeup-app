function uploadImage(input){
  $("#gif").show();
  $("#upload-img").css("opacity", 0);

  var fd = new FormData();
  fd.append('file', input.files[0]);

  $.ajax({
    url: '/inputphoto',
    type: 'POST',
    data: fd,
    cache: false,
    contentType: false,
    processData: false,
    success: function(data) {
      var filename = data['filename'];
      sessionStorage.imageFilename = filename;
      var skin_color = data['skin-color'];
      sessionStorage.skinColor = skin_color;
      $("#gif").hide();
      $("#upload-img").css("opacity", 100);
      $("#skin-color").css('background-color', skin_color);
      $("#upload-img").attr('src', filename);
    }
  });
}

$(document).ready(function() {
  if (sessionStorage.imageFilename) {
    $("#upload-img").attr('src', sessionStorage.imageFilename);
    $("#skin-color").css('background-color', sessionStorage.skinColor);
  }
  if (sessionStorage.eye) {
    $("#eye-input").val(sessionStorage.eye);
  }
  if (sessionStorage.age) {
    $("#age-input").val(sessionStorage.age);
  }
  $("#file-upload").on('change', function(){
    uploadImage(this);
  });
  $("#eye-input").on('change', function(){
    sessionStorage.eye = $("#eye-input").val();
  });
  $("#age-input").on('change', function(){
    sessionStorage.age = $("#age-input").val();
  });
});
