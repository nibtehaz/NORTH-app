var data_per_page = 8;
var all_data = {}, cur_data = {}, fields, seq_found;
var selected_model, selected_cluster;

function init(model) {
    selected_model = model;

    $.get(`http://127.0.0.1:5000/models`, function (data, status) {

        var models = '';

        if (data['models'].length == 0) {
            document.location.href = "/trainfolder?error=error"
        }

        for (var i = 0; i < data['models'].length; i++) {
            if (model == data['models'][i]) {
                models += `<option value="${data['models'][i]}" selected>${data['models'][i]}</option>`;
            }
            else {
                models += `<option value="${data['models'][i]}" >${data['models'][i]}</option>`;
            }
        }

        document.getElementById('model_select').innerHTML = models;

        var elems = document.querySelectorAll('select');
        var instances = M.FormSelect.init(elems, {});

        init_model(model)
    });
}

function init_model(model) {
    selected_model = model;

    $.get(`http://127.0.0.1:5000/listclusters?model=${model}`, function (data, status) {

        console.log(data);

        var cluster = '';

        for (var i = 0; i < data['clusters'].length; i++) {
            if (i == 0) {
                cluster += `<option value="${data['clusters'][i]}" selected>${data['clusters'][i]}</option>`;
            }
            else {
                cluster += `<option value="${data['clusters'][i]}" >${data['clusters'][i]}</option>`;
            }
        }

        document.getElementById('cluster_select').innerHTML = cluster;

        var elems = document.querySelectorAll('select');
        var instances = M.FormSelect.init(elems, {});

        init_cluster(model, data['clusters'][0]);
    });
}

function select_model(val) {

    init_model(val);
}

function select_cluster(val) {

    init_cluster(selected_model, val);
}


function init_cluster(model, cluster) {

    selected_cluster = cluster;

    $.get(`http://127.0.0.1:5000/cluster?cluster=${cluster}&model=${model}`, function (data, status) {

        fields = data["column_names"];
        seq_found = data["seq_found"];

        console.log(data);


        for (var i = 0; i < fields.length; i++) {
            all_data[fields[i]] = [];
            cur_data[fields[i]] = [];
        }


        for (var i = 0; i < fields.length; i++) {
            all_data[fields[i]] = data["data"][fields[i]].slice();
            cur_data[fields[i]] = data["data"][fields[i]].slice();
        }


        var slider = document.getElementById('slider');
        slider.max = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();

        var tot_page = document.getElementById('total_page');
        tot_page.value = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();
        $(document).ready(function () {
            M.updateTextFields();
        });


        update_table(1)

    });

}

function search_fields() {
    var gene_name = document.getElementById('gene_name').value;
    var protein_name = document.getElementById('protein_name').value;
    var organism = document.getElementById('organism').value;
    var uniprot_id = document.getElementById('uniprot_id').value;

    var badges = 0;


    if (gene_name.length != 0) {
        badges++;
        var gene_name2 = gene_name.substr(0, gene_name.length);
        if (gene_name.length > 5) {
            gene_name2 = gene_name.substr(0, 5) + '..';
        }
        document.getElementById('filts1').innerHTML = `<a class="waves-effect waves-light btn blue tooltipped" data-position="bottom" data-tooltip="Gene Name : ${gene_name}">Gene Name : ${gene_name2}</a>`;
    }

    else {
        document.getElementById('filts1').innerHTML = '';
    }


    if (protein_name.length != 0) {
        badges++;
        var protein_name2 = protein_name.substr(0, protein_name.length);
        if (protein_name.length > 5) {
            protein_name2 = protein_name.substr(0, 5) + '..';
        }
        document.getElementById('filts2').innerHTML = `<a class="waves-effect waves-light btn green tooltipped" data-position="bottom" data-tooltip="Protein Name : ${protein_name}">Protein Name : ${protein_name2}</a>`;
    }

    else {
        document.getElementById('filts2').innerHTML = '';
    }

    if (organism.length != 0) {
        badges++;
        var organism2 = organism.substr(0, organism.length);
        if (organism.length > 5) {
            organism2 = organism.substr(0, 5) + '..';
        }
        document.getElementById('filts3').innerHTML = `<a class="waves-effect waves-light btn cyan accent-2 tooltipped" data-position="bottom" data-tooltip="Organism : ${organism}">Organism : ${organism2}</a>`;
    }

    else {
        document.getElementById('filts3').innerHTML = '';
    }

    if (uniprot_id.length != 0) {
        badges++;
        var uniprot_id2 = uniprot_id.substr(0, uniprot_id.length);
        if (uniprot_id.length > 5) {
            uniprot_id2 = uniprot_id.substr(0, 5) + '..';
        }

        document.getElementById('filts4').innerHTML = `<a class="waves-effect waves-light btn pink tooltipped" data-position="bottom" data-tooltip="UniProt id : ${uniprot_id}">UniProt id : ${uniprot_id2}</a>`;
    }

    else {
        document.getElementById('filts4').innerHTML = '';
    }

    if (badges != 0) {
        document.getElementById('filts0').innerHTML = `<a class="btn-flat">Search Filters : </a>`;
        document.getElementById('clr_filts').innerHTML = `<a class="waves-effect waves-light btn blue-grey white-text" target="_blank" onclick="clear_filters()">Clear Filters</a>`;
        var elems = document.querySelectorAll('.tooltipped');
        var instances = M.Tooltip.init(elems);
    }

    for (var i = 0; i < fields.length; i++) {
        cur_data[fields[i]] = [];
    }

    var flag;

    for (var i = 0; i < all_data["uniprot_id"].length; i++) {

        if (all_data["gene_name"][i].includes(gene_name) && all_data["protein_name"][i].includes(protein_name) && all_data["organism"][i].includes(organism) && all_data["uniprot_id"][i].includes(uniprot_id)) {

            for (var j = 0; j < fields.length; j++) {
                cur_data[fields[j]].push(all_data[fields[j]][i])
            }
        }

    }

    var slider = document.getElementById('slider');
    slider.max = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();

    var tot_page = document.getElementById('total_page');
    tot_page.value = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();
    $(document).ready(function () {
        M.updateTextFields();
    });


    update_table(1);



}

function clear_filters() {
    document.getElementById('filts0').innerHTML = '';
    document.getElementById('filts1').innerHTML = '';
    document.getElementById('filts2').innerHTML = '';
    document.getElementById('filts3').innerHTML = '';
    document.getElementById('filts4').innerHTML = '';
    document.getElementById('clr_filts').innerHTML = '';

    for (var j = 0; j < fields.length; j++) {
        cur_data[fields[j]] = all_data[fields[j]].slice();
    }

    var slider = document.getElementById('slider');
    slider.max = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();

    var tot_page = document.getElementById('total_page');
    tot_page.value = (Math.ceil(cur_data["uniprot_id"].length / data_per_page)).toString();
    $(document).ready(function () {
        M.updateTextFields();
    });


    update_table(1);
    clear_inps();

}


function clear_inps() {
    document.getElementById('gene_name').value = "";
    document.getElementById('protein_name').value = "";
    document.getElementById('organism').value = "";
    document.getElementById('uniprot_id').value = "";
}

function update_table(page) {

    if (cur_data["uniprot_id"].length == 0) {
        var ele = document.getElementById('tableBody');
        ele.innerHTML = '';
        return;
    }

    var cur_page = document.getElementById('page_no');
    cur_page.value = (page).toString();

    var table_data = "";

    var st = (page - 1) * data_per_page;
    var en = page * data_per_page;
    var extra = 0;

    if (en > cur_data["uniprot_id"].length) {
        extra = en - cur_data["uniprot_id"].length;
        en = cur_data["uniprot_id"].length;
    }

    for (var i = st; i < en; i++) {
        table_data += `<tr><td>${cur_data["gene_name"][i]}</td><td>${cur_data["protein_name"][i]}</td><td>${cur_data["organism"][i]}</td><td>${cur_data["uniprot_id"][i]}</td><td><a class="waves-effect waves-light btn pink" target="_blank" href="http://www.uniprot.org/uniprot/${cur_data["uniprot_id"][i]}">UniProt</a></td></tr>`;
    }

    var ele = document.getElementById('tableBody');
    ele.innerHTML = table_data;

}


function rangeSlide() {

    var slider_val = document.getElementById('slider').value;
    update_table(slider_val)
}


function changePage() {

    var cur_page = document.getElementById('page_no').value;
    document.getElementById('slider').value = cur_page;

    if (cur_page > (Math.ceil(cur_data["uniprot_id"].length / data_per_page))) {
        cur_page = (Math.ceil(cur_data["uniprot_id"].length / data_per_page));
    }

    update_table(cur_page);

}