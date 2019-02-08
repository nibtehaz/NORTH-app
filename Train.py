import pickle
from math import ceil
from ScalableNaiveBayes import ScalableNaiveBayes, breakIntoKmer
from Outlier import random_forest_wrapper
import os
import sqlite3
from Bio import SeqIO
from time import sleep
import time


def write_log(fl_name, msg):

    fp = open(os.path.join('tempdata', fl_name), 'w')
    fp.write(msg)
    fp.close()


def train_nb(model_name, details, data_path, K, n_child, save_seq):

    def read_nb(data_path, model_name, K, save_seq):

        conn = sqlite3.connect(os.path.join(
            'models', model_name, 'database.db'))
        c = conn.cursor()

        X = []
        Y = []

        vocabulary = {}

        files = next(os.walk(data_path))[2]

        fp = open(os.path.join('models', model_name, 'details.txt'), 'w')
        fp.write(details)
        fp.close()

        c.execute('CREATE TABLE column_names (id INTEGER, name VARCHAR(1000))')
        c.execute("INSERT INTO column_names VALUES (0,'uniprot_id')")
        c.execute("INSERT INTO column_names VALUES (1,'gene_name')")
        c.execute("INSERT INTO column_names VALUES (2,'protein_name')")
        c.execute("INSERT INTO column_names VALUES (3,'organism')")

        if(save_seq):

            c.execute("INSERT INTO column_names VALUES (4,'seq')")

        c.execute(
            'CREATE TABLE cluster_details (id INTEGER, name VARCHAR(1000), description VARCHAR(1000))')

        cnt = 0

        write_log('phase1_0.json', '{"name":"startreading","start":"start"}')
        write_log('phase1_1.json', '{"name":"startcluster","start":"start"}')
        write_log('phase1_2.json', '{"name":"startgene","start":"start"}')

        phase1_index = 3

        tot_clst = len(files) - (1 if 'Outliers.fasta' in files else 0)

        for i in range(len(files)):

            filee = files[i]

            if(filee == 'Outliers.fasta'):
                continue

            table_name = filee[0:-6]
            c.execute("INSERT INTO cluster_details VALUES ({},'{}','')".format(
                cnt, table_name))
            cnt += 1

        conn.commit()
        conn.close()

        cnt = 0

        for i in range(len(files)):

            filee = files[i]

            if(filee == 'Outliers.fasta'):
                continue

            table_name = filee[0:-6]

            conn = sqlite3.connect(os.path.join(
                'models', model_name, table_name+'.db'))
            c = conn.cursor()

            cnt += 1

            write_log('phase1_{}.json'.format(str(phase1_index)), str(
                {"name": "readcluster", "current": cnt-1, "total": tot_clst}))
            phase1_index = (phase1_index + 1) % 1000

            if(save_seq):
                c.execute('CREATE TABLE {} (uniprot_id VARCHAR(1000), gene_name VARCHAR(1000), protein_name VARCHAR(1000), organism VARCHAR(1000), seq VARCHAR(10000))'.format(table_name))

            else:
                c.execute(
                    'CREATE TABLE {} (uniprot_id VARCHAR(1000), gene_name VARCHAR(1000), protein_name VARCHAR(1000), organism VARCHAR(1000))'.format(table_name))

            genes = list(SeqIO.parse(os.path.join(data_path, filee), 'fasta'))
            #genes = list(SeqIO.parse('kegg/'+family+'/Fasta/'+file,'fasta'))

            lst_time = time.time()

            for j in range(len(genes)):
                now_time = time.time()

                if((now_time-lst_time) >= 0.1):
                    lst_time = now_time

                    write_log('phase1_{}.json'.format(str(phase1_index)), str(
                        {"name": "readgene", "current": j, "total": len(genes)}))
                    phase1_index = (phase1_index + 1) % 1000

                gene = genes[j]

                X.append(str(gene.seq))
                Y.append(filee[0:-6])

                kmers = breakIntoKmer(str(gene.seq), K).split(' ')

                for kmer in kmers:

                    vocabulary[kmer] = True

                # db
                header = gene.description

                uniprot_id = header.split('|')[1]

                protein_name = header.split('|')[2].split('=')[
                    0][:-3].split(' ')[1:]
                protein_name = ' '.join(protein_name)

                gene_name = ''

                if('GN=' in header):

                    gene_name = header.split('GN=')[1].split(' ')[0]

                organism = header.split('OS=')[1].split(' ')[:2]
                organism = ' '.join(organism)

                if(save_seq):
                    c.execute("INSERT INTO {} VALUES ('{}','{}','{}','{}','{}')".format(
                        table_name, uniprot_id, gene_name, protein_name, organism, str(gene.seq)))

                else:
                    c.execute("INSERT INTO {} VALUES ('{}','{}','{}','{}')".format(
                        table_name, uniprot_id, gene_name, protein_name, organism))

            conn.commit()
            conn.close()

            write_log('phase1_{}.json'.format(str(phase1_index)), str(
                {"name": "readgene", "current": len(genes), "total": len(genes)}))
            phase1_index = (phase1_index + 1) % 1000

        write_log('phase1_{}.json'.format(str(phase1_index)), str(
            {"name": "readcluster", "current": tot_clst, "total": tot_clst}))
        phase1_index = (phase1_index + 1) % 1000

        vSize = len(vocabulary)

        vocabulary = 'garbage'

        write_log('phase1_{}.json'.format(str(phase1_index)),
                  str({"name": "doneread", "done": "done"}))
        phase1_index = (phase1_index + 1) % 1000

        return (X, Y, vSize)

    def parse_nb(X, Y):
        '''
                        Takes [ (X,Y) ... (X,Y)] as input
                        Returns [ ((x1,x2,..,xn),Y) ... ] as output

        '''

        documents = []
        clsMapper = {}
        vocabulary = {}

        total = len(X)

        for i in range(len(X)):

            try:

                documents[clsMapper[Y[i]]][0].append(X[i])

            except:

                clsMapper[Y[i]] = len(clsMapper)
                documents.append(([X[i]], Y[i]))

        X = None
        Y = None

        return (documents, total)

    if(os.path.isdir(os.path.join('models', model_name))):

        old_files = next(os.walk(os.path.join('models', model_name)))[2]

        for old_file in old_files:

            os.unlink(os.path.join('models', model_name, old_file))

    else:
        os.makedirs(os.path.join('models', model_name))

    (X, Y, vSize) = read_nb(data_path, model_name, K, save_seq)

    (documents, total) = parse_nb(X, Y)

    nb = ScalableNaiveBayes(modelName=os.path.join(
        'models', model_name), vSize=vSize, totalData=total, nChild=n_child)

    nb.train(documents, K)

    documents = None


def train_random_forest(data_path, model_name, n_child):

    random_forest_wrapper(data_path, model_name, n_child)


def train_wrapper(model_name, details, data_path, K, n_child, save_seq, train_outlier):

    train_nb(model_name, details, data_path, K, n_child, save_seq)

    if(train_outlier == 'true'):

        train_random_forest(data_path, model_name, n_child)

    else:

        write_log('phase3_0.json', str({"name": "rfdone", "done": "done"}))


def main():
    pass
    # train_nb('dummy','aasasasasas','./sample_data/dummy_clusters',5,5)
    # train_nb('dummy2','12345','./sample_data/dummy_clusters',5,5)


if __name__ == '__main__':
    main()
