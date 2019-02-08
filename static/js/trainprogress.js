var clstr_prcnt = 0;
var gene_prcnt = 0;
var data_prcnt = 0;
var trn_clstr_prcnt = 0;
var trn_gene_prcnt = 0;
var trn_data_prcnt = 0;
var out_gene_prcnt = 0;
var out_prb_prcnt = 0;

var total_clusters = 0;
var train_cluster = 0;


var temp_clstr_prcnt = 0;
var temp_gene_prcnt = 0;
var temp_data_prcnt = 0;
var trn_temp_gene_prcnt = 0;
var out_temp_gene_prcnt = 0;
var out_temp_prb_prcnt = 0;

var started_reading = 0;
var started_cluster = 0;
var started_gene = 0;

var phase1_index = 0;
var phase2_index = 0;
var phase3_index = 0;

var current_phase = 1;


var polling_object;

function init(model, K, nchilds, details, datapath, save_seq, train_outlier) {

    if (train_outlier) {

    }

    $.get(`/trainmodel?model_name=${model}&details=${details}&data_path=${datapath}&K=${K}&n_child=${nchilds}&save_seq=${save_seq}&train_outlier=${train_outlier}`, function (data, status) {
        ;
    });


    setTimeout(function () {
        polling_object = setInterval(function () {
            polling();
        }, 100);
    }, 1000);





    /*var socket = io.connect('http://127.0.0.1:5000/');

        

  

    });

    socket.on('starttrain', function(data) {
        
        
        
    });



    socket.on('done', function(data) {        
        
        socket.disconnect();     
        document.location.href = "/view_models";       
        
    });*/




}

function polling() {

    if (current_phase === 1) {
        phase1();
    }

    else if (current_phase === 2) {
        phase2();
    }

    else if (current_phase === 3) {
        phase3();
    }

    else if (current_phase == 4) {

        clearInterval(polling_object);

        setInterval(() => {
            document.getElementById('donehed').style.visibility = 'visible';
            setInterval(() => {
                document.location.href = "/view_models";

            }, 500);
        }, 500);
    }

}

function phase1() {

    $.get(`http://127.0.0.1:3000/readjson?filepath=phase1_${phase1_index}.json`, function (data, status) {

        if (data["error"] === "error") {
            ;
        }

        else {
            if (data["name"] === "readgene") {

                document.getElementById('rdgenenum').innerHTML = data['current'] + '/' + data['total'];

                temp_gene_prcnt = Math.round(parseFloat(data['current']) / parseFloat(data['total']) * 100.0);



                if (temp_gene_prcnt > gene_prcnt) {
                    gene_prcnt = temp_gene_prcnt;
                    document.getElementById('rdgeneprcnt').innerHTML = `${gene_prcnt}%`;
                    document.getElementById('rdgeneprg').style.width = `${gene_prcnt}%`;
                }

            }

            else if (data["name"] === "readcluster") {

                document.getElementById('rdclstrnum').innerHTML = data['current'] + '/' + data['total'];
                total_clusters = parseInt(data['total']);
                temp_clstr_prcnt = Math.round(parseFloat(data['current']) / parseFloat(data['total']) * 100.0);

                if (temp_clstr_prcnt > clstr_prcnt) {
                    clstr_prcnt = temp_clstr_prcnt;
                    document.getElementById('rdclstrprcnt').innerHTML = `${clstr_prcnt}%`;
                    document.getElementById('rdclstrprg').style.width = `${clstr_prcnt}%`;
                }

                gene_prcnt = 0;
                temp_gene_prcnt = 0;

            }

            else if (data["name"] === "startreading") {

                document.getElementById('rdclstrhed').style.visibility = 'visible';

            }

            else if (data["name"] === "startcluster") {

                document.getElementById('rdclstrtit').style.visibility = 'visible';
                document.getElementById('rdclstrnum').style.visibility = 'visible';
                document.getElementById('rdclstrprgw').style.visibility = 'visible';
                document.getElementById('rdclstrprg').style.width = '0%';
                document.getElementById('rdclstrprcnt').style.visibility = 'visible';

            }

            else if (data["name"] === "startgene") {

                document.getElementById('rdgenetit').style.visibility = 'visible';
                document.getElementById('rdgenenum').style.visibility = 'visible';
                document.getElementById('rdgeneprgw').style.visibility = 'visible';
                document.getElementById('rdgeneprg').style.width = '0%';
                document.getElementById('rdgeneprcnt').style.visibility = 'visible';

            }

            else if (data["name"] === "doneread") {
                current_phase = 2;
            }


            phase1_index = (phase1_index + 1) % 1000;
        }
    });
}

function phase2() {

    $.get(`http://127.0.0.1:3000/readjson?filepath=phase2_${phase2_index}.json`, function (data, status) {

        if (data["error"] === "error") {
            ;
        }

        else {
            if (data["name"] === "traingene") {
                document.getElementById('trngenenum').innerHTML = data['current'] + '/' + data['total'];

                trn_temp_gene_prcnt = Math.round(parseFloat(data['current']) / parseFloat(data['total']) * 100.0);

                if (trn_temp_gene_prcnt > trn_gene_prcnt) {
                    trn_gene_prcnt = trn_temp_gene_prcnt;
                    document.getElementById('trngeneprcnt').innerHTML = `${trn_gene_prcnt}%`;
                    document.getElementById('trngeneprg').style.width = `${trn_gene_prcnt}%`;
                }
            }

            else if (data["name"] === "traincluster") {

                document.getElementById('trnclstrnum').innerHTML = `${train_cluster}/${total_clusters}`;
                temp_clstr_prcnt = Math.round(train_cluster / total_clusters * 100.0);
                document.getElementById('trnclstrprcnt').innerHTML = `${temp_clstr_prcnt}%`;
                document.getElementById('trnclstrprg').style.width = `${temp_clstr_prcnt}%`;
                trn_gene_prcnt = 0;
                train_cluster += 1;

            }


            else if (data["name"] === "starttrain") {

                document.getElementById('trainhed').style.visibility = 'visible';

                document.getElementById('trnclstrtit').style.visibility = 'visible';
                document.getElementById('trnclstrnum').style.visibility = 'visible';
                document.getElementById('trnclstrprgw').style.visibility = 'visible';
                document.getElementById('trnclstrprg').style.width = '0%';
                document.getElementById('trnclstrprcnt').style.visibility = 'visible';

                document.getElementById('trngenetit').style.visibility = 'visible';
                document.getElementById('trngenenum').style.visibility = 'visible';
                document.getElementById('trngeneprgw').style.visibility = 'visible';
                document.getElementById('trngeneprg').style.width = '0%';
                document.getElementById('trngeneprcnt').style.visibility = 'visible';

            }

            else if (data["name"] === "donetrain") {
                current_phase = 3;
            }

            phase2_index = (phase2_index + 1) % 1000;
        }
    });
}

function phase3() {

    $.get(`http://127.0.0.1:3000/readjson?filepath=phase3_${phase3_index}.json`, function (data, status) {

        if (data["error"] === "error") {
            ;
        }

        else {
            if (data["name"] === "extractfeature") {
                document.getElementById('outftrnum').innerHTML = data['current'] + '/' + data['total'];

                out_temp_gene_prcnt = Math.round(parseFloat(data['current']) / parseFloat(data['total']) * 100.0);

                if (out_temp_gene_prcnt > out_gene_prcnt) {
                    out_gene_prcnt = out_temp_gene_prcnt;
                    document.getElementById('outftrprcnt').innerHTML = `${out_gene_prcnt}%`;
                    document.getElementById('outftrprg').style.width = `${out_gene_prcnt}%`;
                }
            }

            else if (data["name"] === "extractprobas") {

                document.getElementById('outprbnum').innerHTML = data['current'] + '/' + data['total'];

                out_temp_prb_prcnt = Math.round(parseFloat(data['current']) / parseFloat(data['total']) * 100.0);

                if (out_temp_prb_prcnt > out_prb_prcnt) {
                    out_prb_prcnt = out_temp_prb_prcnt;
                    document.getElementById('outprbprcnt').innerHTML = `${out_prb_prcnt}%`;
                    document.getElementById('outprbprg').style.width = `${out_prb_prcnt}%`;
                }

            }


            else if (data["name"] === "rfdone") {

                current_phase = 4;
            }

            else if (data["name"] === "startfeatures") {

                document.getElementById('outftrtit').style.visibility = 'visible';
                document.getElementById('outftrnum').style.visibility = 'visible';
                document.getElementById('outftrprgw').style.visibility = 'visible';
                document.getElementById('outftrprg').style.width = '0%';
                document.getElementById('outftrprcnt').style.visibility = 'visible';

            }


            else if (data["name"] === "startrf") {

                document.getElementById('rftit').style.visibility = 'visible';
                document.getElementById('rfnum').style.visibility = 'visible';
                document.getElementById('rfprgw').style.visibility = 'visible';

            }


            else if (data["name"] === "startoutlier") {

                document.getElementById('outlierhed').style.visibility = 'visible';

                document.getElementById('outprbtit').style.visibility = 'visible';
                document.getElementById('outprbnum').style.visibility = 'visible';
                document.getElementById('outprbprgw').style.visibility = 'visible';
                document.getElementById('outprbprg').style.width = '0%';
                document.getElementById('outprbprcnt').style.visibility = 'visible';

            }






            phase3_index = (phase3_index + 1) % 1000;
        }
    });
}
