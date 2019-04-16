import time
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble.forest import RandomForestClassifier
import os
import pickle
from ScalableNaiveBayes import NaiveBayesChild, breakIntoKmer
from Bio import SeqIO
from scipy.stats import kurtosis, skew
import numpy as np
import pandas as pd

np.random.seed(3)

phase3_index = 0
total_genes = 0
ptr_gene = 0


def write_log3(fl_name, msg):

    global phase3_index

    fp = open(os.path.join('tempdata', fl_name), 'w')
    fp.write(msg)
    fp.close()

    phase3_index = (phase3_index+1) % 1000


def extract_probabilities(child_id, data_path, model_name, nChild):

    global ptr_gene

    child = pickle.load(
        open(os.path.join('models', model_name, str(child_id)+'.p'), 'rb'))

    fasta_files = next(os.walk(data_path))[2]

    lst_time = time.time()

    for fasta_file in fasta_files:

        genes = list(SeqIO.parse(os.path.join(data_path, fasta_file), 'fasta'))

        Y = child.predict(genes)

        ptr_gene += len(genes)

        now_time = time.time()

        if((now_time-lst_time) >= 0.1):

            lst_time = now_time

            write_log3('phase3_{}.json'.format(phase3_index), str(
                {"name": "extractprobas", "current": str(ptr_gene//nChild), "total": str(total_genes)}))

        if(fasta_file == 'Outliers.fasta'):

            pickle.dump(Y, open(os.path.join('tempdata', 'anomalous_features_{}_{}.p'.format(
                fasta_file.split('.')[0], child_id)), 'wb'))

        else:

            pickle.dump(Y, open(os.path.join('tempdata', 'valid_features_{}_{}.p'.format(
                fasta_file.split('.')[0], child_id)), 'wb'))


def feature_extraction(nChild, data_path):

    global ptr_gene

    ptr_gene = 0

    fasta_files = next(os.walk(data_path))[2]

    X = []
    Y = []

    lst_time = time.time()

    for fasta_file in fasta_files:

        clstr_probs = []

        for child_id in range(1, nChild+1):

            if(fasta_file == 'Outliers.fasta'):

                probs = pickle.load(open(os.path.join('tempdata', 'anomalous_features_{}_{}.p'.format(
                    fasta_file.split('.')[0], child_id)), 'rb'))
                os.remove(os.path.join('tempdata', 'anomalous_features_{}_{}.p'.format(
                    fasta_file.split('.')[0], child_id)))

            else:

                probs = pickle.load(open(os.path.join('tempdata', 'valid_features_{}_{}.p'.format(
                    fasta_file.split('.')[0], child_id)), 'rb'))
                os.remove(os.path.join('tempdata', 'valid_features_{}_{}.p'.format(
                    fasta_file.split('.')[0], child_id)))

            if(len(clstr_probs) == 0):

                for i in range(len(probs)):

                    clstr_probs.append([])

            for gene in range(len(probs)):

                ptr_gene += 1

                now_time = time.time()

                if((now_time-lst_time) >= 0.1):

                    lst_time = now_time

                    write_log3('phase3_{}.json'.format(phase3_index), str(
                        {"name": "extractfeature", "current": str(ptr_gene//(nChild*2)), "total": str(total_genes)}))

                for clsID in probs[gene]:

                    if(clsID == 'max' or clsID == 'maxClass'):
                        continue

                    else:
                        clstr_probs[gene].extend(probs[gene][clsID])

        for gene in range(len(clstr_probs)):

            ptr_gene += 1

            now_time = time.time()

            if((now_time-lst_time) >= 0.1):

                lst_time = now_time

                write_log3('phase3_{}.json'.format(phase3_index), str(
                    {"name": "extractfeature", "current": str(ptr_gene//(nChild*2)), "total": str(total_genes)}))

            clstr_probs[gene] = np.array(clstr_probs[gene])
            clstr_probs[gene] = clstr_probs[gene] - np.min(clstr_probs[gene])
            clstr_probs[gene] = clstr_probs[gene] / np.max(clstr_probs[gene])
            # clstr_probs[gene].sort()

            mean = np.mean(clstr_probs[gene])
            std = np.std(clstr_probs[gene])
            summ = np.sum(clstr_probs[gene])
            sk = skew(clstr_probs[gene])
            kur = kurtosis(clstr_probs[gene])

            x = [mean, std, summ, sk, kur]

            X.append(x)

            if(fasta_file == 'Outliers.fasta'):

                Y.append(0)

            else:

                Y.append(1)

    return (X, Y)


def random_forest_wrapper(data_path, model_name, nChild):

    global total_genes
    total_genes = 0
    global phase3_index
    phase3_index = 0
    global ptr_gene
    ptr_gene = 0

    write_log3('phase3_{}.json'.format(phase3_index), str(
        {"name": "startoutlier", "start": "start"}))

    fasta_files = next(os.walk(data_path))[2]

    for fasta_file in fasta_files:

        genes = list(SeqIO.parse(os.path.join(data_path, fasta_file), 'fasta'))

        total_genes += len(genes)

    for child_id in range(1, nChild+1):

        extract_probabilities(child_id, data_path, model_name, nChild)

    write_log3('phase3_{}.json'.format(phase3_index), str(
        {"name": "extractprobas", "current": str(total_genes), "total": str(total_genes)}))

    write_log3('phase3_{}.json'.format(phase3_index), str(
        {"name": "startfeatures", "start": "start"}))

    (X, Y) = feature_extraction(nChild, data_path)

    write_log3('phase3_{}.json'.format(phase3_index), str(
        {"name": "extractfeature", "current": str(total_genes), "total": str(total_genes)}))

    write_log3('phase3_{}.json'.format(phase3_index),
               str({"name": "startrf", "start": "start"}))

    rf = RandomForestClassifier(n_estimators=10)

    rf.fit(X, Y)

    pickle.dump(rf, open(os.path.join('models', model_name, 'rf.p'), 'wb'))

    write_log3('phase3_{}.json'.format(phase3_index),
               str({"name": "rfdone", "done": "done"}))


def main():

    pass


if __name__ == '__main__':
    main()
