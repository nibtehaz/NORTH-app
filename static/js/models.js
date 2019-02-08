var update_model = '';
var delete_model = '';

function init() {
    $.get(`http://127.0.0.1:5000/models`, function (data, status) {
        console.log(data);
        console.log(data['models']);

        if (data['models'].length == 0) {
            document.location.href = "/trainfolder?error=error"
        }

        var models = '';

        for (var i = 0; i < data['models'].length; i++) {
            models += `
                        <li class="collection-item">
                            <div class="row">
                                <div class="col s6">
                                    <a class="btn-flat transparent black-text">${data['models'][i]}</a>
                                </div>
                                <div class="col s2">
                                    <a class="waves-effect waves-light btn teal" onclick="show_details('${data['models'][i]}')">Details</a>
                                </div>
                                <div class="col s2">
                                    <a class="waves-effect waves-light btn light-blue accent-3" href="/view_databases?model=${data['models'][i]}">Database</a>
                                </div>
                                <div class="col s2">
                                    <a class="waves-effect waves-light btn red accent-3" onclick="delete_prompt('${data['models'][i]}')">Delete</a>
                                </div>
                            </div>
                        </li>`
        }

        document.getElementById('list_models').innerHTML = models;

        var elems = document.querySelectorAll('select');
        var instances = M.FormSelect.init(elems, {});
    });
}

function show_details(model_name) {

    document.getElementById('model_name_modal').innerHTML = model_name;

    $.get(`http://127.0.0.1:5000/view_details?model=${model_name}`, function (data, status) {

        document.getElementById('model_details_modal').value = data;

        var elem = document.querySelector('#modal1');
        var instance = M.Modal.init(elem);
        update_model = model_name;
        instance.open();

    });
}

function confirm() {
    var elem = document.querySelector('#modal2');
    var instance = M.Modal.init(elem);
    instance.open();
}

function update() {
    var details2 = document.getElementById('model_details_modal').value;

    $.get(`/update_details?model=${update_model}&details=${details2}`, function (data, status) {

        console.log(data);

        document.location.href = `/view_models`;

    });
}

function delete_prompt(model_name) {

    document.getElementById('delmdlnm').innerHTML = model_name;

    var elem = document.querySelector('#modal3');
    var instance = M.Modal.init(elem);
    delete_model = model_name;
    instance.open();


}

function delete_() {

    $.get(`/deletemodel?model=${delete_model}`, function (data, status) {
        document.location.href = "/view_models";
    });

}