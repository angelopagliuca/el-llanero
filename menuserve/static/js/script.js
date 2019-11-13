

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

csrftoken = getCookie('csrftoken');

function changeQuantity(ele) {

  $.ajaxSetup ({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

  var item_id = ele.value;
  $.ajax({
    type: 'POST',
    url: 'ajax/change-quantity/',
    data: {
      'item_id': item_id, 'operation': ele.id,
    },
    dataType: 'json',
    success: function (data) {
      document.getElementById(item_id + ":quantity").innerHTML = data.quantity;
      if (data.quantity <= 0) {
        var divname = "itemdiv:" + item_id;
        elem = document.getElementById(divname);
        elem.parentNode.removeChild(elem);
      }
    }
  });
}
