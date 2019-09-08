function renderSection(title, data) {
    var shell = $(`<div class="card my-1" id="${title.toLowerCase()}">
<div class="card-header">${title}</div>
<div class="my-body p-2">
<table class="lines">
<tbody></tbody>
</table>
</div>
</div>`);
    var tbl = shell.find('table.lines tbody');
    _.each(data, function(lines, stop) {
        _.each(lines, function(arrivals, line) {
            var line_span = `<span class=""><img class="line-icon" alt="${line}" title="${line}" src="assets/images/${line.toLowerCase()}.svg" /></span>`;

            tbl.append(`<tr>
<td class="">${stop}<td/>
<td class="px-2">${line_span}<td/>
<td class="">${_.map(_.first(arrivals, 3), function(e) { return e['wait_time'] }).join(', ')}<td/>

<tr/>`);
        });
    });
    return shell;
}

function getLocation(callback) {
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
          callback(position);
      }, function(err) {
          alert(err.message);
      });
  } else {
      alert("doesn't work without location");
  }
}

function render($el, data) {
    $el.append(renderSection("Uptown", data['Uptown']));
    $el.append(renderSection("Downtown", data['Downtown']));
}

function setLatLngAndRefresh() {
    var url_string = window.location.href;
    var url = new URL(url_string);
    var latitude = url.searchParams.get("latitude");
    var longitude = url.searchParams.get("longitude");

    if (latitude && longitude) {
        window.latitude = latitude;
        window.longitude = longitude;
        refresh();
    } else {
        getLocation(function(pos) {
            window.latitude = pos.coords.latitude;
            window.longitude = pos.coords.longitude;
            refresh();
        });
    }
}

function refresh() {
    $("#refresh-notice").html("Refreshing...");
    $.getJSON({
        url: "trains.json",
        data: { latitude: window.latitude,
                longitude: window.longitude }
    }).done(function(data) {
        $("#contents").html("");
        render($("#contents"), data);
        $("#refresh-notice").html("");
    });
}

$(document).ready(function() {
    setLatLngAndRefresh();
    $("#refresh").on('click', function() {
        refresh();
        return false;
    });
});
