var max_item = 12;
var panel = '<div class="col-sm-3">\
    <div class="panel panel-default my_panel">\
      <div class="panel-body">\
	<a href="#" class="close" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a>\
        <img alt="" src="img/temp.jpg" class="panel-product-img img-responsive center-block" />\
      </div>\
      <div class="panel-footer">\
        <h3 class="product_name" class="col-sm-11"></h3>\
        <p class="brand_name">\
        </p>\
      </div>\
    </div>\
  </div>';

function display_panels(data, panel_holder) {
  for (var i in data['productid']) {
    var mu_el = document.createElement('div');
    mu_el.setAttribute('class', 'mu-panel');
    mu_el.innerHTML = panel;
    mu_el.getElementsByClassName('product_name')[0].innerText = data['product_name'][i];
    mu_el.getElementsByClassName('brand_name')[0].innerText = data['brand_name'][i];
    var img_path = 'img/product/product-' + data['productid'][i] + '.jpg';
    mu_el.getElementsByClassName('panel-product-img')[0].setAttribute('src', img_path);
    mu_el.setAttribute('data-val', data['productid'][i]);
    panel_holder.append(mu_el);
  }
}

function fetch_popular() {
  var offset = 0;
  if (sessionStorage.offset) {
    offset = Number(sessionStorage.offset);
  }
  insert_preferences();
  $("#panel-holder").children().remove();
  $.ajax({
   type: "POST",
   contentType: "application/json; charset=utf-8",
   url: "/popular",
   async: true,
   data: JSON.stringify({"offset": offset}),
   success: function (data) {
     var pop = JSON.parse(data);
     var panel_holder = document.getElementById('panel-holder');
     display_panels(pop, panel_holder);
     activate_handlers();
     sessionStorage.offset = offset + 12;
   },
   error: function (err) {
     console.log(err);
   }
 });
}

function fetch_all_products() {
  $.ajax({
     type: "GET",
     contentType: "application/json; charset=utf-8",
     url: "/allproducts",
     async: true,
     success: function (data) {
       data = JSON.parse(data);
       for (var key in data["product_name"]) {
         var name = data["product_name"][key];
         var value = data["productid"][key];
         var option = $("<option>");
         option.attr("data-val", value);
         option.attr("value", name);
         $('#product-list').append(option);
       }
     },
     error: function (err) {
       console.log(err);
     }
   });
}

function fetch_product(pid) {

  $.ajax({
     type: "POST",
     contentType: "application/json; charset=utf-8",
     url: "/product",
     async: true,
     data: JSON.stringify({'pid': pid}),
     success: function (data) {
       if ($("#panel-holder").children().length >= max_item) {
         insert_preferences();
         $("#panel-holder").children().remove();
       }
       var prod = JSON.parse(data);
       var panel_holder = document.getElementById('panel-holder');
       display_panels(prod, panel_holder);
       activate_handlers();
     },
     error: function (err) {
       console.log(err);
     }
   });

}


function insert_preferences() {
  var loves = [];
  if (sessionStorage.likes) {
    loves = JSON.parse(sessionStorage.likes);
  }
  var chosen = $('.loved');
  for (var i = 0; i < chosen.length; i++) {
    loves.push(chosen[i].getAttribute('data-val'));
  }

  var dislikes = [];
  if (sessionStorage.dislikes) {
    dislikes = JSON.parse(sessionStorage.dislikes);
  }
  var chosen = $('.disliked');
  for (var i = 0; i < chosen.length; i++) {
    dislikes.push(chosen[i].getAttribute('data-val'));
  }
  sessionStorage.likes = JSON.stringify(loves);
  sessionStorage.dislikes = JSON.stringify(dislikes);
}

function activate_handlers(){
  $('.mu-panel').click(function(e) {
    e.preventDefault();
    if ($(e.target).is($('.glyphicon'))) {
      if (!$(this).hasClass('loved')) {
        $(this).toggleClass('disliked');
        $(this).find('glyphicon').addClass('glyphicon-remove');
        $(this).find('glyphicon').removeClass('glyphicon-heart');
      }
    } else {
      $(this).removeClass('disliked');
      $(this).toggleClass('loved');
      if ($(this).hasClass('loved')){
        $(this).find('.glyphicon').removeClass('glyphicon-remove');
        $(this).find('.glyphicon').addClass('glyphicon-heart');
      } else {
        $(this).find('.glyphicon').removeClass('glyphicon-heart');
        $(this).find('.glyphicon').addClass('glyphicon-remove');
      }
    }
  });
}

 $(document).ready(function() {
   fetch_all_products();
   if (sessionStorage.productsSeen) {
     fetch_popular(Number(sessionStorage.productsSeen));
   } else {
     fetch_popular(0);
   }
   $('#product-input').keyup(function(e){
     if (e.keyCode == 13) {
       value = $("#product-input").val();
       option_el = $( "option[value='" + value + "']" );
       fetch_product(option_el.attr("data-val"));
     }

   });
   $('#done').click(function(e) {
     e.preventDefault();
     insert_preferences();
     window.location = '/dashboard';
   });
 });
