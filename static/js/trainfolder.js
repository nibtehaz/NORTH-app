var tot_clstr = 0;
var pth = '';

var outlier_found = false;

function open_file_dialog() {


    $.get("http://127.0.0.1:3000/filed", function (data, status) {

        pth = data[0];

        $.get(`/listfiles?path=${pth}`, function (data, status) {

            console.log(data);

            tot_clstr = data["numclstr"];

            if (data["numclstr"] == 0) {

                document.getElementById('nmclstr').innerHTML = "Please Select a Valid Directory with Fasta Files";
                return;
            }

            document.getElementById('nmclstr').innerHTML = `${data["numclstr"]} Clusters Found`;

            var clusters = `${data["clusters"][0]}`;

            for (var i = 1; i < data["clusters"].length; i++) {
                clusters += `&nbsp;&nbsp;,&nbsp;&nbsp;${data["clusters"][i]}`;
            }

            document.getElementById('lstclstr').innerHTML = clusters;

            if (data["outlier"]) {
                document.getElementById('otlr').innerHTML = 'Outliers.fasta File Found';
                outlier_found = true;
            }

            else {
                document.getElementById('otlr').innerHTML = 'No Outliers.fasta File Found';
            }

            document.getElementById('otlr').style.marginBottom = "100px";

            document.getElementById('inptblk').style.visibility = 'visible';
            document.getElementById('inptblk').innerHTML =
                `<div class="col s12">
            <h5 id="otlr" style="text-align:center">Model Settings</h5>
        </div>

        <div class="input-field col s6 offset-s3 tooltipped" data-position="right" data-tooltip="Name of the model should be unique.">
            <input id="model_name" type="text">
            <label for="model_name">Model Name</label>
        </div>

        <div class="input-field col s3 offset-s3 tooltipped" data-position="top" data-tooltip="Value of K in the K-mers. Small values of K are likely to underfit the data,<br> whereas large values of K tend to overfit and requires more memory.">
            <input type="number" id="k" min="1" max="10" onchange="check_k()">
            <label for="k">Value of K</label>
        </div>

        <div class="input-field col s3 tooltipped" data-position="top" data-tooltip="Number of child processes to use in the Naive Bayes model.<br> More child processes reduces ram requirement but consumes more time.">
            <input type="number" id="nchild" min="1" max="5">
            <label for="nchild">Number of Child Processes</label>
        </div>

        <div class="input-field col s6 offset-s3 tooltipped" data-position="top" data-tooltip="Optional Description about the Model">
            <textarea id="details" class="materialize-textarea"></textarea>
            <label for="details">Model Description (Optional)</label>
        </div>

        <div class="col s3 offset-s3 switch tooltipped" data-position="top" data-tooltip="Save the gene gene sequences in the database?<br> This would require more memory.">
            <label style="color:black">
                Save Sequence in Database
                <input type="checkbox" id="save_seq">
                <span class="lever"></span>
            </label>
        </div>



        <div class="col s3 switch tooltipped" data-position="top" data-tooltip="Train a custom outlier detection model with the Outliers.fasta file?<br> Otherwise the default model will be deployed.">
            <label style="color:black">
                Train Custom Outlier Detection
                <input type="checkbox" ${outlier_found ? '' : 'disabled'} id="train_outlier" >
                <span class="lever"></span>
            </label>
        </div>

        <div class="col s12">
            <h1 style="text-align:center"><a onclick="start_training()" class="btn pink lighten-1">Start Training</a></h1>
        </div>
    `

            document.getElementById('k').value = `${5}`;
            document.getElementById('nchild').value = `${Math.ceil(data["numclstr"] / 25)}`;

            M.updateTextFields();

            var elems = document.querySelectorAll('.tooltipped');
            var instances = M.Tooltip.init(elems, {});


        });

    });
}

function check_nchild() {

    var ele = document.getElementById('nchild');

    if (ele.value > tot_clstr) {
        ele.value = tot_clstr;
        M.toast({ html: 'Value of Child Processes can not be more than number of clusters' })
    }

    if (ele.value < 1) {
        ele.value = 1;
        M.toast({ html: 'Value of Child Processes can not be less than 1' })
    }
}

function check_k() {

    var ele = document.getElementById('k');

    if (ele.value > 10) {
        ele.value = 10;
        M.toast({ html: 'Value of K should not be more than 10' })
    }

    if (ele.value < 1) {
        ele.value = 1;
        M.toast({ html: 'Value of K can not be less than 1' })
    }
}

function start_training() {

    var model_name = document.getElementById('model_name').value;

    if (model_name.length === 0) {
        M.toast({ html: `Model Name Can not be empty` })
        return;
    }

    $.get(`/checkmodel?model=${model_name}`, function (data, stat) {
        console.log(data);

        if (data['invalid']) {
            M.toast({ html: `There is already a model named ${model_name}` });
            return;
        }

        else {
            document.location.href = `/trainmodelpage?model_name=${model_name}&details=${document.getElementById("details").value}&data_path=${pth}&K=${document.getElementById('k').value}&n_child=${document.getElementById('nchild').value}&save_seq=${document.getElementById('save_seq').checked}&train_outlier=${document.getElementById('train_outlier').checked}`;
        }
    });

}