from tqdm import tqdm
from Bio import SeqIO
import os
import numpy as np
import pickle


def breakIntoKmer(inp, k):

    out = ''

    for i in range(k-1, len(inp)):

        for j in range(1, k+1):

            out += inp[i-k+j]

        out += ' '

    return out[:-1]


def readData(family, path, saveFile, nClasses=250, minCnt=None, K=5):

    X = []
    Y = []

    try:
        os.makedirs(os.path.join('clusters', family+str(nClasses)))
    except:
        pass

    vocabulary = {}

    files = next(os.walk(path))[2]
    lenli = []

    if(minCnt == None):

        for file in tqdm(files, total=len(files)):

            genes = list(SeqIO.parse(os.path.join(path, file), 'fasta'))
            lenli.append(len(genes))

        lenli.sort()

        print(lenli[0], lenli[-nClasses], lenli[-1])

        lenli[-nClasses] = max(lenli[-nClasses], 20)

        for file in tqdm(files, total=len(files)):

            members = ''

            genes = list(SeqIO.parse(os.path.join(path, file), 'fasta'))

            if(len(genes) < lenli[-nClasses]):

                continue

            np.random.shuffle(genes)

            for gene in genes:

                # X.append(str(gene.seq))
                # Y.append(file[0:6])

                members += gene.description + '\n'

                #kmers = breakIntoKmer(str(gene.seq),K).split(' ')

                # for kmer in tqdm(kmers,total=len(kmers)):

                #		vocabulary[kmer] = True

            fp = open(os.path.join('clusters', family +
                                   str(nClasses), file[0:6]+'.txt'), 'w')
            fp.write(members)
            fp.close()

        vSize = len(vocabulary)

    else:

        for file in tqdm(files, total=len(files)):

            genes = list(SeqIO.parse(os.path.join(path, file), 'fasta'))

            if(len(genes) < minCnt):

                continue

            for gene in genes:

                kmers = breakIntoKmer(str(gene.seq), K).split(' ')

                for kmer in tqdm(kmers, total=len(kmers)):

                    vocabulary[kmer] = True

        vSize = len(vocabulary)

        vocabulary = 'garbage'

        for file in tqdm(files, total=len(files)):

            genes = list(SeqIO.parse(os.path.join(path, file), 'fasta'))

            if(len(genes) < minCnt):

                continue

            np.random.shuffle(genes)

            for gene in genes:

                X.append(str(gene.seq))
                Y.append(file[0:6])

    print(set(Y))

    print(len(set(Y)))

    print(vSize)

    pickle.dump((X, Y, vSize), open(saveFile, 'wb'))


def main():
    readData('all', '../Ortholog/kegg/completed/all/Fasta', 'all.p', K=5)


if __name__ == '__main__':
    main()
