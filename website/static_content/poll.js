let syncedInterval = setTimeout(function () { // run function after 1000 ms
}, 1000);

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

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            var csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function () {
    console.log("Starting");
    setup();
});

function createRun(run, id) {
    template = "<div class=\"card\"><div class=\"card-body\" id=\"run-" +
        run + "\"><p class=\"card-text text-muted empty-run\">Bars will appear here.</p></div></div>";
    $("#project-"+id).append(template);
}

function createBar(bar) {
    $("#run-"+bar['run']+" .empty-run").remove();
    let style = "";
    if (bar['comp']) {
        style = " bg-success";
    } else if (bar['err']) {
        style = " bg-danger";
    }
    let template = "<div class=\"row\"><p class=\"col-2 mb-0\">" +
        bar['name'] +
        "</p><div class=\"col\"><div class=\"progress\"><div id=\"bar-" +
        bar['id'] +
        "\" class=\"progress-bar" +
        style +
        "\" role=\"progressbar\" style=\"width: " +
        bar['perc'] +
        "%;\" aria-valuenow=\"" +
        bar['val'] +
        "\" aria-valuemin=\"0\" aria-valuemax=\"" +
        bar['max'] +
        "\">" +
        bar['perc'] +
        "%</div></div></div></div>";
    $("#run-"+bar['run']).append(template);
}

function updateDisplay(data) {
    console.log(data)
    ts = data['ts']
    if ('runs' in data) {
        $(".empty-projects").remove()
        for (let key in data['runs']) {
            createRun(key, data['runs'][key]);
        }
    }
    if ('new' in data) {
        for (let key in data['new']) {
            createBar(data['new'][key]);
        }
    }
    for (let key in data['u']) {
        let value = data['u'][key];
        let bar = $('#bar-' + key);
        bar.css("width", value['perc'] + "%");
        bar.prop("aria-valuenow", value['val']);
        bar.text(value['perc'] + "%")
        if ("comp" in value) {
            bar.addClass("bg-success");
        } else {
            bar.removeClass("bg-success");
            if ("err" in value) {
                bar.addClass("bg-danger");
            } else {
                bar.removeClass("bg-danger");
            }
        }
    }
}

function sync_status() {
    clearTimeout(syncedInterval);
    $("#sync-indicator").addClass('fa-spin')
    syncedInterval = setTimeout(function () { // run function after 1000 ms
        unspin();
    }, 1000);
}

function unspin() {
    console.log("Unspinned")
    $("#sync-indicator").removeClass('fa-spin')
}

function check() {
    $.ajax({
        url: '/api/status/',
        dataType: 'json',
        type: 'get',
        data: {'since': ts},
        success: updateDisplay,
    })
}

function setup() {
    let poll = function () {
        check();
    };
    let pollInterval = setInterval(function () { // run function every 500 ms
        poll();
    }, 1000);
    poll(); // also run function on init
}
