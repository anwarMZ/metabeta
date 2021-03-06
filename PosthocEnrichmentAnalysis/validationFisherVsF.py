"""
testing to what extend the Fisher's exact test and F-measure coincide wrt. significance for a given contingency table:
Approach:
Overarching grid search for significance thresholds for both tests,
For each significance threshold setting:
    Consider representative category and cluster sizes, calculate all possible TP/FP/TN/FN tables and decide
    measure when each test would call this significantly enriched,
    count agreement (up to 91.6%, but for very high Fisher Significance (30) only, and 0.2 ), correlation
    disagreement stems predominantly from scenarios where Fisher's exact test considers a case significant and the F-score does not (green bars).
meaning that the cases our F-measure test flags as significant is a strict subset of those flagged significant by Fisher's exact test.

"""

from scipy.stats import fisher_exact, pearsonr
from math import log
import numpy as np
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

def prf(tp,fp,fn):
    p = float(tp)/(tp+fp)
    r = float(tp)/(tp+fn)
    f1 = 2*p*r/(p+r) 
    return p,r,f1

def fip(envoSize, clusterSize, tp):
    fn = envoSize - tp
    fp = clusterSize - tp
    tn = n - (tp + fn + fp)
    fi = fisher_exact([[tp,fn], [fp, tn]])[1]
    fscore = prf(tp, fp, fn)[-1]
    return fi, fscore

def significanceComparison(fisherScore, fscore, fisherScoreSignificance=10, fscoreSignificance=.3):
    if fisherScore > 0: ## should not be negative, but sometimes due to rounding errors happens and triggers math domain error
        logfi = -log(fisherScore, 10)
        return int(logfi>fisherScoreSignificance), int(fscore>fscoreSignificance)
    else:
        return 1, int(fscore>fscoreSignificance)
    

def agreement(significanceBitvectors):
    """Percentage agreement between the vector of tuples"""
    return sum([int(i==j) for i,j in significanceBitvectors])/float(len(significanceBitvectors))

def fisherSigni(significanceBitvectors):
    """Percentage of cases where Fisher claims significance but not v.v."""
    return sum([int(i==1 and j==0) for i,j in significanceBitvectors])/float(len(significanceBitvectors))

def fSigni(significanceBitvectors):
    """Percentage of cases where F-score claims significance but not v.v."""
    return sum([int(i==0 and j==1) for i,j in significanceBitvectors])/float(len(significanceBitvectors))

def compareFisherF(fisherScoreSignificance, fscoreSignificance):
    totalSigniFisher, totalSigniF = [], []
    for envoSize in [10, 100, 500, 1000][:3]: ## consider representative category sizes, i.e. how many samples have a particular envo annotation
        for clusterSize in [5,10,20,50,100,200,500,1000][:-1]: ## consider representative cluster sizes, from rel. small clusters to very large ones
            fips =  [fip(envoSize, clusterSize,tp) for tp in range(1, min(envoSize,clusterSize)+1)] # consider all contingency tables
            significanceBitvectors = [significanceComparison(fi,f,fisherScoreSignificance=fisherScoreSignificance, fscoreSignificance=fscoreSignificance) for fi,f in fips]
            v1, v2 = zip(*significanceBitvectors)
            totalSigniFisher += v1
            totalSigniF += v2
            #print agreement(significanceBitvectors), fisherSigni(significanceBitvectors), fSigni(significanceBitvectors) ,pearsonr(v1, v2)[0]
    totalZipped = zip(totalSigniFisher, totalSigniF)
    return len(totalZipped), agreement(totalZipped), fisherSigni(totalZipped), fSigni(totalZipped), pearsonr(totalSigniFisher, totalSigniF)[0]

n = 10000
precalc = False
d = {}
dis1 = {}
dis2 = {}
if not precalc:
    for fi in [2,3,5,10,15,20,25,30]:
        for f1 in [.2, .3, .4, .5, .8]:
            cf = compareFisherF(fi, f1)
            d[(fi,f1)] = 1-cf[1]
            dis1[(fi,f1)] = cf[3]
            dis2[(fi,f1)] = cf[2]
            print "\t".join(map(str, (fi, f1) + cf))
else:        
    results = """2	0.2	120	0.633333333333	0.366666666667	0.0	0.320154220869
    2	0.3	120	0.466666666667	0.533333333333	0.0	0.228479512909
    2	0.4	120	0.35	0.65	0.0	0.175370729667
    2	0.5	120	0.266666666667	0.733333333333	0.0	0.138655728255
    2	0.8	120	0.1	0.9	0.0	0.0455960752588
    3	0.2	120	0.675	0.325	0.0	0.408611468447
    3	0.3	120	0.508333333333	0.491666666667	0.0	0.291607429153
    3	0.4	120	0.391666666667	0.608333333333	0.0	0.223824915309
    3	0.5	120	0.308333333333	0.691666666667	0.0	0.176965715389
    3	0.8	120	0.141666666667	0.858333333333	0.0	0.0581940766433
    5	0.2	120	0.725	0.266666666667	0.00833333333333	0.48934927581
    5	0.3	120	0.575	0.425	0.0	0.380176966871
    5	0.4	120	0.458333333333	0.541666666667	0.0	0.291806959993
    5	0.5	120	0.375	0.625	0.0	0.230715277427
    5	0.8	120	0.208333333333	0.791666666667	0.0	0.0758692863634
    10	0.2	120	0.808333333333	0.141666666667	0.05	0.613944898003
    10	0.3	120	0.708333333333	0.275	0.0166666666667	0.517209850431
    10	0.4	120	0.608333333333	0.383333333333	0.00833333333333	0.412805203365
    10	0.5	120	0.541666666667	0.458333333333	0.0	0.357318411594
    10	0.8	120	0.375	0.625	0.0	0.117501940896
    15	0.2	120	0.858333333333	0.05	0.0916666666667	0.718077757035
    15	0.3	120	0.775	0.175	0.05	0.571098116863
    15	0.4	120	0.708333333333	0.266666666667	0.025	0.483642632821
    15	0.5	120	0.658333333333	0.333333333333	0.00833333333333	0.428606803029
    15	0.8	120	0.508333333333	0.491666666667	0.0	0.154876615156
    20	0.2	120	0.858333333333	0.00833333333333	0.133333333333	0.743898942961
    20	0.3	120	0.808333333333	0.116666666667	0.075	0.607504048052
    20	0.4	120	0.741666666667	0.208333333333	0.05	0.478313063797
    20	0.5	120	0.708333333333	0.266666666667	0.025	0.428667515267
    20	0.8	120	0.591666666667	0.408333333333	0.0	0.18311354945
    25	0.2	120	0.783333333333	0.0	0.216666666667	0.640735690891
    25	0.3	120	0.816666666667	0.0666666666667	0.116666666667	0.609847918162
    25	0.4	120	0.766666666667	0.15	0.0833333333333	0.461394089832
    25	0.5	120	0.733333333333	0.208333333333	0.0583333333333	0.363445507165
    25	0.8	120	0.666666666667	0.325	0.00833333333333	0.109730366439
    30	0.2	120	0.725	0.0	0.275	0.559230392968
    30	0.3	120	0.841666666667	0.025	0.133333333333	0.669956085557
    30	0.4	120	0.791666666667	0.108333333333	0.1	0.482505080994
    30	0.5	120	0.758333333333	0.166666666667	0.075	0.351591095429
    30	0.8	120	0.708333333333	0.275	0.0166666666667	0.017767661134"""


    for line in results.split('\n'):
        fi,f1,agree,fis, f1s = np.array(map(float,line.split("\t")))[[0,1,3,4,5]]
        d[(fi,f1)] = 1-agree
        dis1[(fi,f1)] = f1s
        dis2[(fi,f1)] = fis

x = [2,3,5,10,15,20,25,30]
y = [.2, .3, .4, .5, .8]
xx,yy = np.meshgrid(x,y)        
z = np.zeros(xx.shape)

for idx, x0 in enumerate(x):
    for idy, y0 in enumerate(y):
        z[idy,idx] = d[(x0,y0)]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(xx, z, yy)
#surf = ax.plot_surface(xx, yy, z, cmap=cm.coolwarm)
for y0 in y:
    disagreementFromFisher = [dis2[(x0,y0)] for x0 in x]
    ax.bar(x, disagreementFromFisher, zs=y0, color='g', alpha = 0.8) 
    ax.bar(x, [dis1[(x0,y0)] for x0 in x], zs=y0, bottom=disagreementFromFisher, color='r', alpha = 0.8)

ax.set_xlabel('Fisher Significance')
ax.set_ylabel('Disagreement')
ax.set_zlabel('F-Significance')
plt.show()

