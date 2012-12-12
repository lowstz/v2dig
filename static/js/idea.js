function Comment_click() {
    document.getElementById('cs_comment').className = "input";
}

function Comment_no() {
    document.getElementById('cs_comment').className = "input small";
}

function getObject(objectId) {
    if (document.getElementById && document.getElementById(objectId)) {
        return document.getElementById(objectId);
    } else if (document.all && document.all(objectId)) {
        return document.all(objectId);
    } else if (document.layers && document.layers[objectId]) {
        return document.layers[objectId];
    } else {
        return false;
    }
}

function focusTab(n) {
    for (var i = 1; i <= 3; i++) {
        if (i == n) {
            getObject('focusTable' + i).style.display = 'inline';
        } else {
            getObject('focusTable' + i).style.display = 'none';
        }
    }
}

function progress() {
    var str = document.getElementById("progress").title;
    document.getElementById("progress").innerHTML = str;
}

window.onload  =  
function() {
    focusTab(1);
    progress();
}
