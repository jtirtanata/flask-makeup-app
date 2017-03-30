
function search() {
  var data = {}
  data['category'] = $("#category").val();
  if (sessionStorage.age) {
    data['age'] = sessionStorage.age;
  }
  if (sessionStorage.eye) {
    data['eye_color'] = sessionStorage.eye;
  }
  if (sessionStorage.likes) {
    data['likes'] = sessionStorage.likes;
  }
  if (sessionStorage.dislikes) {
    data['dislikes'] = sessionStorage.dislikes;
  }
  if (sessionStorage.skinColor) {
    data['skin_color'] = sessionStorage.skinColor;
  }
  data = JSON.stringify(data);
  $.ajax({
   type: "POST",
   contentType: "application/json; charset=utf-8",
   url: "/recommendations",
   async: true,
   data: data,
   success: function (data) {
     $('#panel-holder').children().hide();
     var sug = JSON.parse(data);
     $('#panel-holder').children().remove();
     var panel_holder = document.getElementById('panel-holder');

     display_panels(sug, panel_holder);
   },
   error: function (err) {
     console.log(err);
   }
 });
}

var panel = '<div class="col-sm-3">\
    <div class="panel panel-default my_panel">\
      <div class="panel-body">\
        <img alt="" src="img/temp.jpg" class="panel-product-img img-responsive center-block" />\
      </div>\
      <div class="panel-footer">\
        <h3 class="product_name"></h3>\
        <p class="brand_name">\
        </p>\
      </div>\
    </div>\
  </div>';
function display_panels(data, panel_holder) {
  this.cur_data = data;
  for (var i in data['productid']) {
    var mu_el = document.createElement('div');
    mu_el.setAttribute('class', 'mu-panel');
    mu_el.innerHTML = panel;
    mu_el.getElementsByClassName('product_name')[0].innerText = data['product_name'][i];
    mu_el.getElementsByClassName('brand_name')[0].innerText = data['brand_name'][i];

    var img_path = 'img/product/product-' + data['productid'][i] + '.jpg';
    mu_el.getElementsByClassName('panel-product-img')[0].setAttribute('src', img_path);
    if ("url" in data) {
      var swatch = document.createElement('img');
      swatch.setAttribute('class', 'swatch-color');
      var swatch_path = 'img/swatch/' + data['sku'][i] + '.jpg';
      swatch.setAttribute('src', swatch_path);
      mu_el.getElementsByClassName('panel-body')[0].prepend(swatch);
    }
    mu_el.setAttribute('data-val',i);
    panel_holder.append(mu_el);
  }
  activate_handlers();
}

function activate_handlers() {
  $('.my_panel').on('click', function(){
    pid = this.parentElement.parentElement.getAttribute('data-val');
    pid = parseInt(pid);
    $('#product-modal').attr('data-val', window.cur_data['productid'][pid]);

    var img_path = 'img/product/product-' + window.cur_data['productid'][pid] + '.jpg';
    $('.modal-product-img').first().attr('src', img_path);
    $('.modal-title').first().text(window.cur_data['product_name'][pid]);
    $('#modal-product-brand').text(window.cur_data['brand_name'][pid]);
    $('#details').text(window.cur_data['details'][pid]);
    $("#product-modal").modal(function(){});
    $("#buy-link").attr("href", window.cur_data["product_url"][pid]);
    if ("url" in window.cur_data) {
      var swatch = $('.modal-swatch-img').first();
      var swatch_path = 'img/swatch/' + window.cur_data['sku'][pid] + '.jpg';
      swatch.attr('src', swatch_path);
      swatch.show();
      var sku = window.cur_data['sku'][pid];
      $('.modal-title').first().append('<span>' + sku + '</span>');

    } else {
      $('.modal-swatch-img').first().hide();
    }
  });
}
