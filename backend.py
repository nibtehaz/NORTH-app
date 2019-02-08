from ScalableNaiveBayes import ScalableNaiveBayes
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import kurtosis, skew
import numpy as np
import sqlite3


def numChilds(model, nJobs):

    nJobs = int(nJobs)

    nb = pickle.load(open(os.path.join('models', model, 'model.p'), 'rb'))

    jobs = []

    for j in range(nJobs):
        jobs.append([])

    for i in range(nb.nChild):

        jobs[i % nJobs].append(nb.childs[i])

    return {'nChild': nb.nChild,
            'childs': nb.childs,
            'jobs': jobs}


def childPredict(seq, model, fls, ind):

    fls = fls.split(',')

    maxx = None
    maxxClass = None
    all_proba = []

    for fl in fls:

        child = pickle.load(open(os.path.join('models', model, fl), 'rb'))
        Y = child.predict([seq])
        if(maxx == None):
            maxx = Y[0]['max']
            maxxClass = Y[0]['maxClass']

        elif(maxx < Y[0]['max']):
            maxx = Y[0]['max']
            maxxClass = Y[0]['maxClass']

        all_proba.extend(Y[0]['all_proba'])

        child = None

    return {'cluster': maxxClass,
            'proba': maxx,
            'all_proba': all_proba,
            'ind': ind}


def get_members(model, cluster):

    conn = sqlite3.connect(os.path.join('models', model, 'database.db'))
    c = conn.cursor()

    c.execute('SELECT name FROM column_names ORDER BY id')
    rows = c.fetchall()

    column_names = []
    sql_fields = ''
    seq_found = False

    for dat in rows:

        if(dat[0] == 'seq'):
            seq_found = True
            continue

        column_names.append(dat[0])

        sql_fields += dat[0]+','

    sql_fields = sql_fields[:-1]

    conn.close()

    conn = sqlite3.connect(os.path.join('models', model, cluster+'.db'))
    c = conn.cursor()

    data = {}

    c.execute('SELECT {} FROM {}'.format(sql_fields, cluster))
    rows = c.fetchall()

    for col in column_names:
        data[col] = []

    for dat in rows:

        for dat_i in range(len(dat)):

            data[column_names[dat_i]].append(dat[dat_i])

    return {"column_names": column_names,
            "data": data,
            'seq_found': seq_found
            }


def get_clusters(model):

    conn = sqlite3.connect(os.path.join('models', model, 'database.db'))
    c = conn.cursor()

    c.execute('SELECT name FROM cluster_details ORDER BY id')
    rows = c.fetchall()

    clusters = []

    for r in rows:

        clusters.append(r[0])

    return {'clusters': clusters}


def get_cluster_details(model, cluster):

    conn = sqlite3.connect(os.path.join('models', model, 'database.db'))
    c = conn.cursor()

    c.execute(
        "SELECT description FROM cluster_details WHERE name='{}'".format(cluster))
    row = c.fetchone()

    return {'details': row[0]}


def anomaly_detection(model, proba_str):

    proba = []

    chunks = proba_str.split(',')

    for ch in chunks:
        proba.append(float(ch))

    proba = np.array(proba)
    proba = proba - np.min(proba)
    proba = proba / np.max(proba)

    mean = np.mean(proba)
    std = np.std(proba)
    summ = np.sum(proba)
    sk = skew(proba)
    kur = kurtosis(proba)

    x = [mean, std, summ, sk, kur]

    mdl = pickle.load(open(os.path.join('models', model, 'rf.p'), 'rb'))

    yp = mdl.predict([x])[0]

    return {'valid': str(yp)}


def get_all_models():

    try:
        os.makedirs('models')
    except:
        pass

    models = next(os.walk('models'))[1]

    return {'models': models}


def view_model_details(model):

    try:
        fp = open(os.path.join('models', model, 'details.txt'), 'r')
        details = fp.read()
        fp.close()
        return details
    except:
        fp = open(os.path.join('models', model, 'details.txt'), 'w')
        fp.close()
        return ""


def update_model_details(model, details):

    fp = open(os.path.join('models', model, 'details.txt'), 'w')
    details = fp.write(details)
    fp.close()
    return "done"


def list_all_files(pth):

    files = next(os.walk(pth))[2]

    clusters = []
    outlier = False

    for fl in files:

        if(fl == 'Outliers.fasta'):
            outlier = True

        elif(fl[-6:] == '.fasta'):
            clusters.append(fl[:-6])

    clusters.sort()

    return {"clusters": clusters,
            "outlier": outlier,
            "numclstr": len(clusters)}


if __name__ == '__main__':

    rf = pickle.load(open('rf.p', 'rb'))
    inp = '-1435.3239658715136,-1452.8098346864176,-1446.4124947574696,-1431.4458457057347,-1443.0438442304892,-1433.997816565932,-1429.7838514899922,-1435.9617099112431,-1426.8138426755368,-1439.5559066831845,-1431.5630671897827,-1443.5832359723515,-1412.8738403668547,-1429.4091120673781,-1458.3686869532487,-1407.1074359994313,-1437.1237040996834,-1452.610011452579,-1440.6472363021762,-1432.9350495025826,-1424.2908633617938,-1446.7706646906072,-1462.097636077135,-1448.8692071835537,-1435.4622844218165,-1459.7054786912606,-1432.0866941841066,-1421.6225167054056,-1463.5634193802737,-1391.108399897975,-1443.8451645895477,-1445.633392037018,-1437.229734134647,-1459.972294347388,-1456.0753436388613,-1447.6378002030526,-1391.729366909126,-1429.2016651281917,-1449.1291277855842,-1435.0930895821277,-1422.322981905764,-1452.633565157529,-1451.548502102014,-1440.7126896812688,-1458.435820344992,-1451.9521069392938,-1465.2320096780807,-1424.071462051956,-1434.8193600757072,-1428.1133865784625,-1363.0475186650954,-1454.987983171973,-1427.503541856377,-1439.13389259903,-1432.3532672633098,-1427.3014313249314,-1460.6491275863966,-1437.6362719811839,-1453.4350098372497,-1456.1273260828905,-1457.5531698464179,-1435.8183828140154,-1450.8304483463296,-1431.8497936135286,-1418.0149618633689,-1460.0885464064243,-1430.8193173074515,-1449.491696656906,-1437.9446680554804,-1439.4851075167485,-1450.5419366403157,-1450.187041143424,-1463.8022536579197,-1447.2177224045768,-1445.7612917839997,-1446.0602678573462,-1442.1622164732848,-1456.0403044224227,-1458.0365728998306,-1443.070092929411,-1434.5972705733677,-1435.5159847756993,-1438.226546867675,-1459.7674439879747,-1463.7309544007087,-1449.302325052698,-1461.3936296533402,-1415.4588949859665,-1446.834448810127,-1456.104050844344,-1433.4010675261889,-1396.0818619432087,-1455.049393298784,-1440.602782905948,-1449.4585960703016,-1436.7858941202971,-1431.20064820771,-1437.925978769648,-1455.4901724246201,-1424.9648235852321,-1463.6084637268254,-1442.2370893223194,-1445.1952927149475,-1451.7961811471057,-1410.1297920867357,-1455.059695841656,-1446.818232957338,-1436.1612414091828,-1459.9981542044902,-1425.535349576333,-1462.2608200600175,-1446.2697451764311,-1461.4796700783065,-1455.5217761884905,-1425.9080376698412,-1448.5647256366956,-1458.2005603381524,-1430.0091309833042,-1426.297190677092,-1442.6414860161058,-1433.0203985075195,-1447.24374573665,-1442.8397781480344,-1444.4306945376989,-1379.9597045725932,-1439.4258405115959,-1460.0437840079983,-1417.3227005174922,-1428.6786067618762,-1417.9192136821182,-1461.0510320827639,-1455.9826252632738,-1465.2346995587372,-1463.2123974199226,-1464.721036455746,-1431.9889399575345,-1428.763889208129,-1436.5508749904902,-1433.3765294145517,-1443.9972348000717,-1463.8879438167019,-1423.342899750684,-1452.6494471787464,-1440.0895351196996,-1446.120703352838,-1442.2318923439007,-1457.682170373966,-1440.1756069049136,-1353.10746296295,-1441.1029774796687,-1442.609877552206,-1456.971437824022,-1443.1593382100818,-1406.5510100172537,-1451.7362609658949,-1451.8062981715343,-1456.7550881870927,-1433.3028587430185,-1459.0497823518938,-1439.7182033958761,-1445.4759511901218,-1445.5044924088934,-1441.1208502968168,-1449.0040377649334,-1414.0402404447932,-1439.0595257906573,-1401.7732375869143,-1405.531255528503,-1428.362093178741,-1464.9879668720625,-1443.2200148211743,-1442.7388037457772,-1441.9662015538506,-1438.78814648035,-1445.0048190189207,-1442.4290416393555,-1460.988855997671,-1369.2797078691785,-1444.9585329461636,-1445.4371345771885,-1451.8969572101937,-1441.2695518463943,-1440.055937215277,-1441.1992536117052,-1462.5475127109376,-1433.970555076797,-1464.375737819638,-1460.59542340798,-1444.2135164706851,-1428.3653404266597,-1422.5592605978459,-1448.6625637997322,-1440.7316936271072,-1440.5505106316477,-1451.8071757316986,-1428.8042890252689,-1447.116452554283,-1438.3123659104144,-1449.401474553439,-1446.7737657262896,-1455.721699971797,-1439.4017967950138,-1432.0476360785829,-1428.1887141319112,-1426.5330609439259,-1450.1977685521856,-1434.772895693567,-1421.6003940919875,-1452.0074648979871,-1458.050558068668,-1447.416117166556,-1380.9500011511109,-1452.4891767931801,-1453.420936104167,-1434.4616028001692,-1428.7331749474613,-1441.590538328838,-1432.3456563325265,-1375.4621193754963,-1447.6452010476828,-1439.3757343278182,-1446.2018216538697,-1447.9423794465195,-1415.1822273837329,-1439.5844554336493,-1457.9033283716335,-1452.119988269274,-1417.092083848611,-1442.4779904132279,-1455.734770596271,-1456.758108890262,-1441.7857709581083,-1454.3665834183148,-1462.9417777432739,-1463.570951847833,-1456.01829061202,-1445.0005362748673,-1411.6790569012078,-1424.272957141533,-1439.3853302474479,-1429.5351008608775,-1447.924402354549,-1439.2356852849439,-1463.22511545047,-1451.610778838155,-1450.4363822640364,-1443.287154036898,-1434.695000250199,-1423.513442482429,-1441.7642626932918'
    anomaly_detection(rf, inp)
