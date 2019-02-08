var nJobs = 1;

function process(seq, model) {

    $.get(`http://127.0.0.1:5000/njobs?model=${model}&nJobs=${nJobs}`, function (data, status) {

        console.log(data);

        var start = 0;
        var joined = 0;

        var d = new Date();
        var n = d.getTime();

        var results = [];

        var done = 0;

        for (var i = 0; i < nJobs; i++) {

            $.get(`http://127.0.0.1:5000/parallel?seq=${seq}&model=${model}&fls=${data["jobs"][i]}&ind=${i}`, function (data, status) {
                console.log(data);
                results[data['ind']] = data;

                var d2 = new Date();
                var n2 = d2.getTime();

                console.log((n2 - n) / 1000);
                done++;

            });
        }

        var ele = setInterval(function () {
            console.log(done);

            if (done == nJobs) {

                clearInterval(ele);

                var maxx = results[0]['proba'];
                var maxxClass = results[0]['cluster'];
                var all_proba = [];

                for (var i2 = 0; i2 < nJobs; i2++) {

                    if (maxx < results[i2]['proba']) {
                        maxx = results[i2]['proba'];
                        maxxClass = results[i2]['cluster'];
                    }

                    all_proba = all_proba.concat(results[i2]['all_proba']);

                }

                var all_proba = all_proba.toString();

                $.get(`/findrf?model=${model}`, function (data, status) {

                    if (data['rf']) {
                        $.get(`http://127.0.0.1:5000/anomaly?model=${model}&proba_str=${all_proba}`, function (data, status) {


                            if (data["valid"] === "1") {
                                document.location.href = `/results?seq=${seq}&model=${model}&cluster=${maxxClass}`;
                            }

                            else {
                                document.location.href = `/outlier?seq=${seq}`;
                            }

                        });
                    }

                    else {
                        document.location.href = `/results?seq=${seq}&model=${model}&cluster=${maxxClass}`;
                    }

                })



            }

        }, 500);


    });


}
