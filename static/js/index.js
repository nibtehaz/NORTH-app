var selected_model = -1;

var file_mode = 1;

function get_models() {
    $.get(`http://127.0.0.1:5000/models`, function (data, status) {

        if (data['models'].length == 0) {
            document.location.href = "/trainfolder?error=error"
        }

        console.log(data);
        console.log(data['models'])

        var models = '<option value="-1" disabled selected>Please Select a Model</option>';

        for (var i = 0; i < data['models'].length; i++) {
            models += `<option value="${data['models'][i]}" >${data['models'][i]}</option>`
        }

        models += `<option value="Train New Model">Train New Model</option>`;

        document.getElementById('model_select').innerHTML = models;

        console.log(models);


        var elems = document.querySelectorAll('select');
        var instances = M.FormSelect.init(elems, {});
    });
}

function select_model(val) {
    if (val === "Train New Model") {
        document.location.href = "/trainfolder";
    }

    else {
        selected_model = val;
        document.getElementById("model").value = val;
    }
}

function fmlyBtn(btnID) {

    // old button
    var button = document.getElementById(family);

    button.classList.remove("waves-light");
    button.classList.add("waves-teal");
    button.classList.add("btn-flat");

    // update family
    family = btnID;

    // new button

    var button = document.getElementById(family);

    button.classList.remove("waves-teal");
    button.classList.remove("btn-flat");
    button.classList.add("waves-light");


    //console.log(family);
    //console.log(button.classList);
}

function rangeSlide() {
    slider = document.getElementById('slider');

    var arr = [10, 50, 100, 150, 200, 250];

    for (var i = 1; i < arr.length; i++) {
        if (arr[i - 1] <= slider.value && slider.value <= arr[i]) {
            if ((slider.value - arr[i - 1]) < (arr[i] - slider.value)) {
                slider.value = arr[i - 1];
            }

            else {
                slider.value = arr[i];
            }
        }
    }

    sliderValue = document.getElementById('sliderValue');

    sliderValue.text = slider.value;
}


function rdoBtn(rdoID) {
    if (rdoID == 'radio1') {
        file_mode = 1;
        document.form_control.action = "#";
        document.form_control.method = "GET";
        document.form_control.enctype = "";
        document.getElementById("sequenceArea").placeholder = "Please enter the protein sequence of the gene";
    }

    else if (rdoID == 'radio2') {
        file_mode = 2;
        document.form_control.action = "#";
        document.form_control.method = "GET";
        document.form_control.enctype = "";
        document.getElementById("sequenceArea").placeholder = ">tr|Q9C666|Q9C666_ARATH Acyl-CoA N-acyltransferases (NAT) superfamily protein OS=Arabidopsis thaliana OX=3702 GN=At1g26220 PE=2 SV=1\nMFLGGTISTPPASLRLRSTLNPQNAVTQSSSQATFPAAMQRKPPSYSISDEDLESRGFLLRRTTEGLNLDQLNSVFAAVGFPRRDTAKIEVALQHTDALLWVEYEKTRRPVAFARATGDGVFNAIIWDVVVDPSFQSCGLGKAVMERLIEDLQVKGICNIALYSEPRVLGFYRPLGFVSDPDGIKGMVFIRKQRNKK";
    }

    else if (rdoID == 'radio3') {
        file_mode = 3;
        document.form_control.action = "#";
        document.form_control.method = "GET";
        document.form_control.enctype = "";
        document.getElementById("sequenceArea").placeholder = "Please enter the UniProt id";
    }

    else if (rdoID == 'radio4') {
        file_mode = 4;
        document.form_control.action = "http://127.0.0.1:5000/";
        document.form_control.method = "POST";
        document.form_control.enctype = "multipart/form-data";
        document.getElementById("sequenceArea").placeholder = "Please upload a text file in fasta format";
    }
}

function submit() {
    if (typeof (selected_model) === typeof (-1)) {
        alert("Please Select a Model")
        return;
    }

    if (file_mode === 4) {
        document.getElementById("form_control").submit();
    }

    else {
        var seq = document.getElementById('sequenceArea').value;

        if (seq.length == 0) {
            seq = 'MFLGGTISTPPASLRLRSTLNPQNAVTQSSSQATFPAAMQRKPPSYSISDEDLESRGFLLRRTTEGLNLDQLNSVFAAVGFPRRDTAKIEVALQHTDALLWVEYEKTRRPVAFARATGDGVFNAIIWDVVVDPSFQSCGLGKAVMERLIEDLQVKGICNIALYSEPRVLGFYRPLGFVSDPDGIKGMVFIRKQRNKK';
        }

        document.location.href = `/submit?seq=${seq}&model=${selected_model}&mode=${file_mode}`;
    }

}