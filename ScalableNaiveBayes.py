import os
from math import log10
import pickle
from math import ceil
import numpy as np
from multiprocessing import Pool
import time

np.random.seed(3)

global phase2_index
phase2_index = 0


def write_log2(fl_name, msg):

    global phase2_index

    fp = open(os.path.join('tempdata', fl_name), 'w')
    fp.write(msg)
    fp.close()

    phase2_index = (phase2_index+1) % 1000


class ScalableNaiveBayes(object):

    def __init__(self, modelName, vSize=0, totalData=0, alpha=1.0, nJobs=1, nChild=30):

        if(os.path.isdir(modelName)):

            pass

        else:

            os.makedirs(modelName)

        self.modelName = modelName
        self.childs = []
        self.nChild = nChild
        self.alpha = alpha
        self.nJobs = nJobs
        self.vSize = vSize
        self.totalData = totalData

    def train(self, data, K, childsToEmploy='All'):

        global phase2_index
        phase2_index = 0

        if(childsToEmploy == 'All'):

            childsToEmploy = self.nChild

        classesPerChild = ceil(len(data) / childsToEmploy)

        write_log2('phase2_0.json', str(
            {"name": "starttrain", "nchild": childsToEmploy, "cpc": classesPerChild}))

        for i in range(1, childsToEmploy+1):

            dataPartition = data[(
                i-1)*classesPerChild: min(i*classesPerChild, len(data))]

            child = NaiveBayesChild(str(i), self.vSize, self.alpha, K)
            child.train(dataPartition, self.totalData)
            pickle.dump(child, open(self.modelName+'/'+str(i)+'.p', 'wb'))
            self.childs.append(str(i)+'.p')

        write_log2('phase2_{}.json'.format(phase2_index), str(
            {"name": "traincluster", "current": "done"}))

        # last child

        #dataPartition = data[(childsToEmploy-1)*classesPerChild : len(data)]

        #child = NaiveBayesChild(str(childsToEmploy),self.vSize,self.alpha)
        # child.train(dataPartition,self.totalData)
        # pickle.dump(child,open(self.modelName+'/'+str(childsToEmploy)+'.p','wb'))
        # self.childs.append(str(childsToEmploy)+'.p')

        write_log2('phase2_{}.json'.format(phase2_index),
                   str({"name": "donetrain", "done": "done"}))

        pickle.dump(self, open(os.path.join(self.modelName, 'model.p'), 'wb'))

    def predict(self, X):
        '''
                Input : X is a list or numpy array
        '''
        pool = Pool(processes=2)

        results = [pool.apply(childwisePredict, args=(
            idd, self.modelName, self.childs, X)) for idd in range(0, self.nChild)]

        maxx = results[0][0]['max']
        maxxClass = results[0][0]['maxClass']

        for i in range(1, self.nChild):

            if(maxx < results[i][0]['max']):

                maxx = results[i][0]['max']
                maxxClass = results[i][0]['maxClass']

        return maxxClass


def breakIntoKmer(inp, k):

    out = ''

    for i in range(k-1, len(inp)):

        for j in range(1, k+1):

            out += inp[i-k+j]

        out += ' '

    return out[:-1]


def childwisePredict(childID, modelName, childs, X):
    '''
            Input : X is a list or numpy array
    '''

    child = pickle.load(open(os.path.join(modelName, childs[childID]), "rb"))

    Y = child.predict(X)

    return Y[:]


class NaiveBayesChild(object):

    def __init__(self, ID, vSize, alpha, K):

        self.classes = []
        self.prior = {}
        self.probabilities = {}
        self.defaultRatio = {}
        self.alpha = alpha
        self.id = ID
        self.vSize = vSize
        self.K = K

    def train(self, data, totalData):

        # print(len(data))
        # print(len(data[0]))

        # print(data)

        global phase2_index

        for docClass in data:

            write_log2('phase2_{}.json'.format(phase2_index), str(
                {"name": "traincluster", "current": "done"}))

            classLabel = docClass[1]

            self.classes.append(classLabel)
            # print(self.classes)

            # to avoid recomputing log10 values again and again
            self.prior[classLabel] = log10(len(data[0]) / totalData)
            self.probabilities[classLabel] = {}

            totalWords = 0

            lst_time = time.time()

            for itext in range(len(docClass[0])):

                now_time = time.time()

                text = docClass[0][itext]

                if((now_time-lst_time) >= 0.1):

                    lst_time = now_time

                    write_log2('phase2_{}.json'.format(phase2_index), str(
                        {"name": "traingene", "current": itext, "total": len(docClass[0])}))

                tokenizedText = breakIntoKmer(text, self.K).split(' ')

                for word in tokenizedText:

                    # print(word)

                    totalWords += 1

                    try:

                        self.probabilities[classLabel][word] += 1

                    except:  # word is not present

                        self.probabilities[classLabel][word] = 1

            write_log2('phase2_{}.json'.format(phase2_index), str(
                {"name": "traingene", "current": len(docClass[0]), "total": len(docClass[0])}))

            ikmer = 0

            for word in self.probabilities[classLabel]:

                self.probabilities[classLabel][word] = log10((self.probabilities[classLabel][word] + self.alpha) / (
                    totalWords + self.alpha*self.vSize))  # to avoid recomputing log10 values again and again

                ikmer += 1

            # to avoid recomputing log10 values again and again
            self.defaultRatio[classLabel] = log10(
                (self.alpha) / (totalWords + self.alpha*self.vSize))

    def predict(self, X):
        '''
                Input : list or numpy array of texts
                Output : predicts the output classeses in the following format
                                        [ (classLabel, probability) ... for x in X ]

        '''

        Y = []

        try:

            for i in (range(len(X))):

                x = breakIntoKmer(X[i], self.K).split(' ')

                y = {}
                y['max'] = None
                y['all_proba'] = []

                for className in (self.classes):

                    prediction = self.prior[className]

                    for word in (x):

                        try:

                            prediction += self.probabilities[className][word]

                        except:

                            prediction += self.defaultRatio[className]

                    #y[className] = prediction
                    y['all_proba'].append(prediction)

                    if(type(y['max']) == type(None)):

                        y['max'] = prediction
                        y['maxClass'] = className

                    elif(y['max'] < prediction):

                        y['max'] = prediction
                        y['maxClass'] = className

                Y.append(y)

            return Y

        except Exception as e:

            print(e)

            print('Pass as input list or numpy array of texts')


def main():

    pass


if __name__ == '__main__':

    main()
