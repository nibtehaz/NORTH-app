#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from flask import Flask, render_template, send_from_directory, request, jsonify
from werkzeug import secure_filename
from backend import *
from input_processing import *
from Train import train_wrapper
import sys
import multiprocessing

template_folder = os.path.join('templates')
static_folder = os.path.join('static')
app = Flask(__name__, template_folder=template_folder,
            static_folder=static_folder)
app.config['UPLOAD_FOLDER'] = ''

'''if getattr(sys, 'frozen', False):                                                                                                                                     
	template_folder = os.path.join('templates')                                                                                                  
	static_folder = os.path.join('static')                                                                                                       
	app = Flask(__name__, template_folder = template_folder, static_folder = static_folder)
	app.config['UPLOAD_FOLDER'] = '''''


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template("index.html", page_name='Ortholog Query', err=True)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template("index.html", page_name='Ortholog Query', err=True)

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        seq = parse_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if(seq == 'error'):
            return render_template("index.html", page_name='Ortholog Query', err=True)

        return render_template("processing.html", seq=seq, model=request.form["model"])

    else:
        return render_template("index.html", page_name='Ortholog Query')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/submit')
def submit():

    seq = None

    if(request.args.get("mode") == '1'):
        print(1)
        seq = request.args.get("seq")

    elif(request.args.get("mode") == '2'):
        print(2)
        seq = parse_fasta(request.args.get("seq"))

    elif(request.args.get("mode") == '3'):
        print(3)
        seq = obtain_sequence_from_uniprot(request.args.get("seq"))

    print(seq)

    return render_template("processing.html", seq=seq, model=request.args.get("model"))


@app.route('/njobs')
def njobs():
    return jsonify(numChilds(model=request.args.get("model"), nJobs=request.args.get("nJobs")))


@app.route('/parallel')
def parallel():
    return jsonify(childPredict(seq=request.args.get("seq"), model=request.args.get("model"), fls=request.args.get("fls"), ind=request.args.get("ind")))


@app.route('/results')
def results():

    return render_template("results.html", seq=request.args.get("seq"), model=request.args.get("model"), cluster=request.args.get("cluster"))


@app.route('/cluster')
def cluster():
    print('*'*10)
    print(request.args.get("model"))
    print('*'*10)
    return jsonify(get_members(model=request.args.get("model"), cluster=request.args.get("cluster")))


@app.route('/listclusters')
def listclusters():
    return jsonify(get_clusters(model=request.args.get("model")))


@app.route('/clusterdetails')
def clusterdetails():
    return jsonify(get_cluster_details(model=request.args.get("model"), cluster=request.args.get("cluster")))


@app.route('/anomaly')
def anomaly_rf():
    return jsonify(anomaly_detection(model=request.args.get("model"), proba_str=request.args.get("proba_str")))


@app.route('/outlier')
def outlier_pg():
    return render_template("anomaly.html", seq=request.args.get("seq"))


@app.route('/models')
def get_models():

    return jsonify(get_all_models())


@app.route('/view_models')
def view_models():

    return render_template("models.html", page_name='Trained Models')


@app.route('/trainfolder', methods=['GET', 'POST'])
def train_folder():

    if(request.args.get("error") == None):
        return render_template('trainfolder.html')

    else:
        return render_template('trainfolder.html', error="error")


@app.route('/trainmodelpage')
def train_page():
    return render_template('trainprogress.html', model=request.args.get('model_name'), details=request.args.get('details'), datapath=request.args.get('data_path'), K=request.args.get('K'), nchilds=request.args.get('n_child'), save_seq=request.args.get('save_seq'), train_outlier=request.args.get('train_outlier'))


@app.route('/trainmodel')
def save_train_met():

    try:
        os.makedirs('tempdata')
    except:
        pass

    K = int(request.args.get('K'))
    n_child = int(request.args.get('n_child'))

    train_meta = {'model_name': request.args.get('model_name'),
                  'details': request.args.get('details'),
                  'data_path': request.args.get('data_path'),
                  'K': K,
                  'n_child': n_child,
                  'save_seq': request.args.get('save_seq'),
                  'train_outlier': request.args.get('train_outlier')}

    #pickle.dump(train_meta, open(os.path.join('tempdata','train_meta.p'),'wb'))
    #train_meta = pickle.load(open(os.path.join('tempdata','train_meta.p'),'rb'))

    train_wrapper(train_meta['model_name'], train_meta['details'], train_meta['data_path'],
                  train_meta['K'], train_meta['n_child'], train_meta['save_seq'], train_meta['train_outlier'])

    return ""


@app.route('/deletemodel')
def delete_model():

    old_files = next(os.walk(os.path.join(
        'models', request.args.get('model'))))[2]

    for old_file in old_files:

        os.unlink(os.path.join('models', request.args.get('model'), old_file))

    os.rmdir(os.path.join('models', request.args.get('model')))

    return ""


@app.route('/findrf')
def find_rf():

    if(os.path.isfile(os.path.join('models', request.args.get('model'), 'rf.p'))):

        return jsonify({'rf': True})

    else:

        return jsonify({'rf': False})


@app.route('/listfiles')
def list_files():

    return jsonify(list_all_files(request.args.get("path")))


@app.route('/view_details')
def view_details():

    return view_model_details(request.args.get('model'))


@app.route('/update_details')
def update_details():

    return update_model_details(request.args.get('model'), request.args.get('details'))


@app.route('/view_databases')
def view_database():

    model = request.args.get('model')

    if(model == None):

        try:
            model = get_all_models()['models'][0]
        except:
            pass

    return render_template("databases.html", page_name='Ortholog Databases', model=model)


@app.route('/checkmodel')
def check_model():

    return jsonify({'invalid': os.path.isdir(os.path.join('models', request.args.get('model')))})


def main():

    multiprocessing.freeze_support()

    try:

        app.run()
        fp = open('strt.txt', 'a')
        fp.close()

    except Exception as e:
        print(e)
        fp = open('err.txt', 'a')
        fp.write(str(e)+'\n')
        fp.close()


if __name__ == '__main__':
    main()
