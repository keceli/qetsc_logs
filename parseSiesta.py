#!/usr/bin/env python
import numpy as np
import logging
import itertools

keys=[
      "Time (sec):",
      " 2:   siesta_forces:",
      " 3:    siesta_solve:",
      " 4:    siesta2qetsc:",
      " 5:  qetsc_setupEPS:",
      " 9:  qetsc_solveEPS:",
      " 8:   qetsc_density:",
      "10:     siesta_misc:"
      ]
def list2Str(list1):
    return str(list1).replace('[','').replace(']','').replace(',','').replace("'","").replace(":","").replace('(','').replace(')','')

def readQETSc(myfile):
    qetsc = True
    kwup  ='10:     siesta_misc:'
    kw    = 'QETSC: Number of ranks       ='
    kw    = '* Running on'
    nrank = int(getValue(kw,myfile))
    kw    = 'QETSC: Number of req. evals  ='
    nreqd = int(getValue(kw,myfile))
    kw    = 'QETSC: Number of ranks/slice ='
    npmat = int(getValue(kw,myfile))
    kw    = 'Time (sec):'
    tall  = float(getValue(kw,myfile))
    kw    = ' 2:   siesta_forces:'
    tforce= float(getValue(kw,myfile))
    kw    = ' 6:  qetsc_solveEPS:'
    tsols = [0.]*4
    tsols[0]  = float(getValue(kw,myfile))
    kw    = ' 6:  qetsc_solve_EPS:'
    tsols[1]  = float(getValue(kw,myfile))
    kw    = ' 6: qetsc_solve_eps:'
    tsols[2]  = float(getValue(kw,myfile))
    kw    = ' 3:    siesta_solve:'
    tsols[3]  = float(getValue(kw,myfile))
    tsol  = max(tsols)
    tup =  float(getValue(kwup,myfile))
    if tsols.index(tsol) == 3 : 
        qetsc = False
        tden=tmax=tmin=tave=tsym=tnum= 0.
    else:    
        tsym,tnum  = getFactTimes(myfile)
        tmax,tmin,tave =getIterTimes(myfile)
        tden = float(getValue(' 8:   qetsc_density:',myfile))
    return myfile.split('/')[-1],nrank,tall,tsol,tforce,npmat,tden,tmax,tmin,tave,tsym,tnum

def getIterTimes(logfile):
    logging.debug("Reading file {0}".format(logfile))
    i = 0
    titers = [0.]*120
    keyword ='QETSC: Iter time'
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(keyword):
                titers[i]=float(line.split()[5])
                i += 1            
    return max(titers),min(titers[0:i]),sum(titers)/i    

def getMaxIterTimes(logfile):
    logging.debug("Reading file {0}".format(logfile))
    i = 0
    titers = [0.]*120
    keyword ='QETSC: Iter time (max)       ='
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(keyword):
                titers[i]=float(line.split()[6])
                i += 1            
    return titers[0:i]

def getNumberofIters(logfile):
    return int(getValue("QETSC: Finished iter         =",logfile))

def getNumberofBins(logfile):
    return int(getValue("QETSC: Number of slices      =",logfile))

def getBinTimes(logfile):
    logging.debug("Reading file {0}".format(logfile))
    iterno = 0
    binno  = 0
    nbin   = getNumberofBins(logfile)
    niter  = getNumberofIters(logfile)
    print nbin, niter
    tbins = np.zeros((niter,nbin))
    keyword ='SLEPc: EPSSolve time ='
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(keyword):
                while line.startswith(keyword):
                    binno=int(line.split()[-2])
                    tbins[iterno,binno] = float(line.split()[-1])
                    line=f.readline()
                iterno += 1            
    return tbins

def getEvalsInBin(evals,bins,iterno,binno):
    return evals[iterno,(evals[iterno,:]>bins[iterno,binno]) 
          & (evals[iterno,:]<bins[iterno,binno+1])]

def getNumberofEvalsPerBin(evals,bins):
    nbin  = bins.shape[1]-1
    niter = bins.shape[0]
    nevals = np.zeros((niter,nbin))
    for i in range(niter):
        for j in range(nbin):
            nevals[i,j]=len(evals[i,(evals[i,:] > bins[i,j])
                                  &(evals[i,:] < bins[i,j+1])])
    return nevals

def getFactTimes(logfile):
    logging.debug("Reading file {0}".format(logfile))
    kwnum='MatCholFctrNum'
    kwsym='MatCholFctrSym'
    
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(kwnum):
                n = int(line.split()[1])
                tall = float(line.split()[3])
                tnum = tall/n
            elif line.startswith(kwsym):
                n = int(line.split()[1])
                tall = float(line.split()[3])
                tsym = tall/n
    return tsym,tnum

def readLogDirectory():
    import glob
    global filename
    for myfile in glob.glob("log.*"):
        print list2Str(readQETSc(myfile))
    return 0

def getValue(keyword,logfile,pos=0,pickfirst=False):
    logging.debug("Reading file {0}".format(logfile))
    value = 0.
    found = False
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(keyword):
                value=line.replace(keyword,'').split()[pos]
                found = True
            elif found and pickfirst:
                break
    return value     

def getValues(logfile):
    keywords=[
       "QETSC: Number of ranks       =",
       "QETSC: Number of slices      =",
       "QETSC: Number of req. evals  =",
       "QETSC: Number of rows (all)  =",
       "QETSC: Number of nonzeros    ="]
    values=[0.0]*len(keywords)
    logging.debug("Reading file {0}".format(logfile))
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            else:
                for i in range(len(keys)):
                    if line.startswith(keys[i]):
                        a=line.replace(keys[i],'').split()
                        values[i]=a[0]
        print logfile, list2Str(values)        
           
    return values     
    
def getBins(logfile):
    nbin   = 1 + getNumberofBins(logfile)
    niter  = getNumberofIters(logfile)
    bins   = np.zeros([niter,nbin])
    eiter  = 0
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(" QETSC: Bins             ="):
                for i in range(nbin):
                    line = f.readline()
                    bins[eiter,i] = float(line.split()[0])
                eiter += 1
    return bins                

def getEigenvalues(logfile):
    neval   = int(getValue("QETSC: Number of req. evals  =",logfile))
    niter  = getNumberofIters(logfile)
    evals   = np.zeros([niter,neval])
    eiter  = 0
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            elif line.startswith(" QETSC: Eigenvalues         ="):
                for i in range(neval):
                    line = f.readline()
                    evals[eiter,i] = float(line.split()[0])
                eiter += 1
    return evals                


def readLogFile(logfile):
    import socket
    errorCode="OK"
    values=[0.0]*len(keys)
    
    logging.debug("Reading file {0}".format(logfile))
    with open(logfile) as f:
        while True:          
            line = f.readline()
            if not line: 
                break
            else:
                for i in range(len(keys)):
                    if line.startswith(keys[i]):
                        a=line.replace(keys[i],'').split()
                        values[i]=a[0] 
        print logfile, list2Str(values)        
           
    return 0     
    
def plotIterTimes(logfile0,logfile2,logfile3,savefile=None):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    titers0 = getMaxIterTimes(logfile0)
    titers2 = getMaxIterTimes(logfile2)
    titers3 = getMaxIterTimes(logfile3)
    tsym,tnum = getFactTimes(logfile)
    maxiter = len(titers0)
    fig, axes = plt.subplots(nrows=1, ncols=1)
    i4=4
    myxrange = [i4+0.5,maxiter+1]
    plt.xlim(myxrange)
    plt.ylim([0,max(titers0)*1.2])
    plt.xlabel('Iteration')
    plt.ylabel('Time (t)')
    x = np.arange(i4+1, maxiter+1, 1.0)
    plt.xticks(x)
    plt.plot(x,titers0[i4:maxiter],ls='none',marker='s',color='k',label='b0:uniform')
    plt.plot(x,titers2[i4:maxiter],ls='none',marker='o',color='r',label='b2:cluster')
    plt.plot(x,titers3[i4:maxiter],ls='none',marker='*',color='b',label='b3:ungap')
    axes.axhline(tsym,color='r')
    axes.axhline(tnum,color='b')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
    
    if savefile:
        plt.savefig(savefile)
    plt.show()
    return

def plotStrong(savefile=None):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    ms=8
#    nranks,tall,tsol,tmat= np.genfromtxt('dataw128.txt', unpack=True,usecols=(1, 2,3,4))
    nranks,tsca= np.loadtxt('datascalapakw128.txt', unpack=True,usecols=(0,1))
    nranksq,tq,tqx= np.loadtxt('datastrongq128.txt', unpack=True,usecols=(0,1, 2))
    plt.plot(nranks,tsca,ls='None', label='ScaLAPACK', marker='s', markersize=ms, mfc='k')
    plt.plot(nranksq,tq,ls='None', label='QETSc', marker='o', markersize=ms, mfc='b')
  #  plt.plot(nranksq,tqx,ls='None', label='QETScX', marker='*', markersize=ms, mfc='c')
    plt.legend(loc='best', ncol=1, fancybox=True, shadow=True)
    plt.xlabel('Number of ranks')
    plt.ylabel('Solution time (s)')
    plt.xlim([0,1050])
    plt.ylim([30,250])
  #  plt.xscale('log',basex=2)
   # plt.yscale('log')
    xticklabel = [ 32,128,256, 512,1024]
    plt.xticks(xticklabel, map(lambda i : "%d" % i, xticklabel))
    if savefile:
        plt.savefig(savefile)
    plt.show()
        
    return

def plotEvalsAndBins(maxiter,evals,bins,savefile=None):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    mineval = np.min(np.min(evals,axis=1))
    maxeval = np.max(np.max(evals,axis=1))
    erange  = maxeval - mineval
    fig, axes = plt.subplots(nrows=1, ncols=1)
    myyrange = [mineval-0.2, maxeval + 0.2]
    myxrange = [0,maxiter+1]
    plt.xlim(myxrange)
    plt.ylim(myyrange)
    plt.xlabel('Iteration')
    plt.ylabel('Eigenvalues (ev)')
    plt.xticks(np.arange(1, maxiter, 1.0))
    for i in range(maxiter):
        plt.plot(np.zeros_like(evals[i,:])+i+1,evals[i,:],ls='none',marker='_',color='b')
        plt.hlines(y=bins[i,:],xmin=i+0.75,xmax=i+1.25,color='r')
    axes.axhline(mineval, color='k',lw=0.1)
    axes.axhline(maxeval, color='k',lw=0.1)
    if savefile:
        plt.savefig(savefile)
    plt.show()
    return

def plotEvalsAndBinsAndTimes(maxiter,evals,bins,tbins,savefile=None):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    mineval = np.min(np.min(evals,axis=1))
    maxeval = np.max(np.max(evals,axis=1))
    maxt    = np.max(np.max(tbins,axis=1))
    erange  = maxeval - mineval
    fig, axes = plt.subplots(nrows=1, ncols=1)
    myyrange = [mineval-0.2, maxeval + 0.2]
    myxrange = [0,maxiter+1]
    plt.xlim(myxrange)
    plt.ylim(myyrange)
    plt.xlabel('Iteration')
    plt.ylabel('Eigenvalues (ev)')
    plt.xticks(np.arange(1, maxiter+1, 1.0))
    mycolors=plt.get_cmap('OrRd')
    mycolors=plt.get_cmap('jet')
    mycolors=plt.get_cmap('RdYlGn_r')
    for i in range(maxiter):
        # Different widths for slices does not look nice
        maxtbin = np.max(tbins[i,:])
        # width   = 0.1 + 0.15*tbins[i,:]/maxtbin
        # plt.hlines(y=bins[i,:],xmin=i+1-width,xmax=i+1+width,color='r')
        plt.plot(np.zeros_like(evals[i,:])+i+1,evals[i,:],ls='none',marker='_',color='k',ms=6)
        plt.hlines(y=bins[i,1:],xmin=i+0.75,xmax=i+1.25,color=mycolors(tbins[i,:]/maxtbin),linewidth=1)
    axes.axhline(mineval, color='k',lw=0.1)
    axes.axhline(maxeval, color='k',lw=0.1)
    if savefile:
        plt.savefig(savefile)
    plt.show()
    return

def plotEvals(maxiter,evals,nslice=None,savefile=None):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    mineval = np.min(np.min(evals,axis=1))
    maxeval = np.max(np.max(evals,axis=1))
    erange  = maxeval - mineval
    fig, axes = plt.subplots(nrows=1, ncols=1)
    myyrange = [mineval-0.1, maxeval + 0.1]
    myxrange = [0,maxiter+1]
    plt.xlim(myxrange)
    plt.ylim(myyrange)
    plt.xlabel('Iteration')
    plt.ylabel('Eigenvalues (ev)')
    plt.xticks(np.arange(1, maxiter, 1.0))
    for i in range(maxiter):
        plt.plot(np.zeros_like(evals[i,:])+i+1,evals[i,:],ls='none',marker='_',color='b')
    axes.axhline(mineval, color='k',lw=0.3)
    axes.axhline(maxeval, color='k',lw=0.3)
    if nslice:
        binsize=erange/nslice
        for i in range(nslice+1):
            axes.axhline(mineval + i*binsize,color='r',lw=0.3)
    if savefile:
        plt.savefig(savefile)
    plt.show()
    return

def plotBins(x,binedges,savefile=None,myc='r'):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    fig, axes = plt.subplots(figsize=[3,5],nrows=1, ncols=1)
    myxrange = [-2.5,0.25]
    plt.ylim(myxrange)
    plt.xlim([-0.05,0.05])
    plt.plot(np.zeros_like(x),x,ls='none',marker='_',color='b')
    #plt.xlim([min(x)-0.2,max(x)+0.2])
    for edge in binedges:
        axes.axhline(edge,color=myc,lw=0.5)
    plt.gca().get_xaxis().set_ticklabels([])
    plt.ylabel('Eigenvalues (ev)')
    plt.title(savefile)
    if savefile:
        plt.savefig('plotBins'+savefile+'.png')
    plt.show()    
    return  

def plotVBins(x,binedges):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return     
    fig, axes = plt.subplots(figsize=[12,2],nrows=1, ncols=1)
    myxrange = [-2.5,0.25]
    plt.xlim(myxrange)
    plt.ylim([-0.05,0.05])
    plt.plot(x,np.zeros_like(x),ls='none',marker='.')
    #plt.xlim([min(x)-0.2,max(x)+0.2])
    for edge in binedges:
        axes.axvline(edge)
    plt.show()    
    return  

def plotIterTimes(logfile0,logfile2,logfile3):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return
    titers0 = getMaxIterTimes(logfile0)
    titers2 = getMaxIterTimes(logfile2)
    titers3 = getMaxIterTimes(logfile3)
    tsym,tnum = getFactTimes(logfile)
    maxiter = len(titers0)
    fig, axes = plt.subplots(nrows=1, ncols=1)

    myxrange = [0,maxiter+1]
    plt.xlim(myxrange)
 #   plt.ylim(myyrange)
    plt.xlabel('Iteration')
    plt.ylabel('Time (t)')
    x = np.arange(1, maxiter+1, 1.0)
    plt.xticks(x)
    plt.plot(x,titers0,ls='none',marker='.',color='k')
    plt.plot(x,titers2,ls='none',marker='o',color='r')
    plt.plot(x,titers3,ls='none',marker='s',color='b')
    axes.axvline(tsym)
    plt.show()
    return

def plotEvalsHor(maxiter,evals):
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return     
    fig, axes = plt.subplots(figsize=[16,8],nrows=1, ncols=1)
    #plt.setp(axes, xlim=myxrange, ylim=myyrange)
    myxrange = [min(evals[:,0])-0.1,max(evals[:,-1])+0.1]
    myxrange = [-2.5,0.0]
    myyrange = [0,maxiter+1]
    plt.xlim(myxrange)
    plt.ylim(myyrange)
    for i in range(maxiter):
        plt.plot(evals[i,:],np.zeros_like(evals[i,:])+i+1,ls='none',marker='.',color='r')
    plt.show()
    return

def getDensityOfStates(eigs,width=0.1,npoint=200):
    """
    Computes density of states (dos) by representing
    `eigs` (eigenvalues) as gaussians of given `width`. 
    Parameters
    ----------
    eigs   : Array of floats
             Eigenvalues required to generate dos
    width  : Width of the gaussian function centered
             at eigenvalues
             eigs and width have the same units.
    npoint : Int
             Number of energy points to compute dos.
    Returns
    -------
    energies : Array of floats
               Energies for which DOS is computed.     
    dos      : Array of floats
               len(dos) = len(energies) = npoints 
               Density of states computed at energies.
               dos has the inverse of the units of energies.
    Notes
    -----
    The mathematical definition of density of states is:
    $D(x) = \frac{1}{N}\sum\limits_n \delta(x-x_n)$,
    where $x_n$ is the $n$th eigenvalue and $N$ is 
    the total number of eigenvalues.
    Here, delta function is represented by a gaussian,i.e.
    $\delta(x) = \frac{1}{a\sqrt{\pi}}\exp(-\frac{x^2}{a^2})$
    """
    b = width * 5.
    energies = np.linspace(min(eigs)-b,max(eigs)+b,num=npoint)
    N = len(eigs)
    w2 = width * width
    tmp = np.zeros(len(energies))
    for eig in eigs:
        tmp += np.exp(-(energies-eig)**2 / w2)
    dos = tmp / (np.sqrt(np.pi) * width * N)    
    return energies, dos

def plotDensityOfStates(energies,dos,units='Hartree',title='DOS'):
    """
    Plots density of states.
    Parameters
    ---------
    energies : Array of floats
               Energies for which DOS is computed.     
    dos      : Array of floats
               len(dos) = len(energies) 
               Density of states computed at energies.
               dos has the inverse of the units of energies
    """
    try:
        import matplotlib.pyplot as plt
    except: 
        Print("Requires matplotlib")
        return     
    assert len(energies) == len(dos), "energies and dos should have the same length"
    plt.figure()
    plt.plot(energies,dos)
    plt.xlabel('Energies ({0})'.format(units))
    plt.ylabel('DOS 1/({0})'.format(units))
    plt.title(title)
    plt.show()
    return
def getClusters(x, crange=1.e-6):
    """
    Given an array of numbers (x) and a threshold for clustering,
    returns an array of clusters, and the multiplicities
    of each cluster.
    Input:
    eigs    - numpy array (dtype='float64')
    chtresh - float (optional)
    Returns:
            - numpy array (dtype='float64')
            - numpy array (dtpye='int32')
    """
    nx          = len(x)
    clusters       = np.zeros(nx)
    multiplicities = np.ones(nx,dtype='int32')
    clusters[0]    = x[0]
    icluster       = 0
    for i in range(1,nx):
        if x[i]-clusters[icluster] < crange:
            multiplicities[icluster] += 1
        else:
            icluster += 1
            clusters[icluster] = x[i]
    ncluster = icluster + 1
    return clusters[0:ncluster], multiplicities[0:ncluster]

def getBinEdges0(x,nbin,binbuffer=0.001):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns uniform width bin edges.
    Parameters
    ----------
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    """
    n    = len(x)
    bins = np.linspace(min(x)-binbuffer,max(x)+binbuffer,nbin+1)
    return bins

def getBinEdges1(x, nbin, rangebuffer=0.1,interval=[0],cthresh=1.e-6):
    """
    Given a list of eigenvalues, (x) and number of subintervals (nbin), 
    returns the boundaries for subintervals such that each subinterval has an average number of eigenvalues.
    Doesn't skip gaps, SLEPc doesn't support it, yet.
    range of x * rangebuffer gives a rangebuffer zone for leftmost and rightmost boundaries.
    """
    x, mults = getClusters(x,cthresh) 
    nx = len(x)
    mean = nx / nbin
    remainder = nx % nbin
    erange = x[-1] - x[0]
    isbuffer = erange * rangebuffer
    b = np.zeros(nbin + 1)
    b[0] = x[0] - isbuffer
    for i in xrange(1, nbin):
        b[i] = (x[mean * i] + x[mean * i - 1]) / 2.
        if remainder > 0 and i > 1:
            b[i] = (x[mean * i + 1] + x[mean * i]) / 2.
            remainder = remainder - 1
    b[nbin] = x[-1] + isbuffer
    if len(interval)==2:
        b[0]  = interval[0]
        b[-1] = interval[1]
    return b

def getBinEdges2(x,nbin,binbuffer=0.001):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns optimum bin edges,
    to reduce number of shifts required for eps
    solve.
    Input:
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    TODO:
    Bisection type algorithms can be used to obtain optimum bin edges.
    Binning score can be used for better optimization of bin edges
    """
    rangex = max(x) - min(x)
    meanbinsize = rangex / float(nbin)
    b = np.zeros(nbin+1)
    maxtrial = 100
    crange = meanbinsize
    i = 0
    while i < maxtrial:
        i += 1
        clusters = getClusters(x,crange=crange)[0]
        ncluster = len(clusters)
        if ncluster > nbin:
            crange = crange * 1.1
        elif ncluster < nbin:    
            crange = crange * 0.9
        else:
            break
    if i == maxtrial :
        Print("Bin optimization failed for bintype 2, switching to bintype 1. Found {0} clusters".format(ncluster))
        Print("Adjust bin edges based on prior knowledge to have a uniform number of eigenvalues in each bin")
        b = getBinEdges1(x,nbin)[0]
    else:
        for i in range(nbin):
            b[i] = clusters[i] - binbuffer
        b[nbin] = max(x) + binbuffer    
    return b

def getBinEdges3(x,nbin,binbuffer=0.001):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns bin edges,
    based on k-means clustering algorithm.
    Parameters
    ----------
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    Notes
    -----
    Requires scikit package.
    Using k-means for 1d arrays is considered to be an overkill.
    However, it seems to me as a practical solution for the binning problem.
    """
    try: 
        from sklearn.cluster import KMeans
    except:
        Print("sklearn.cluster not found.")
    n = len(x)
    b = np.zeros(nbin+1)
    # random_state is used to fix the seed, to avoid random results
    # clusterids is an integer array (with len(x)) returning an index for clusters found.
    clusterids = KMeans(n_clusters=nbin,random_state=17).fit_predict(x.reshape(-1,1))
    assert n == len(clusterids), "Kmeans failed, missing clusters"
    b[0]       = x[0] - binbuffer
    uniqueids  = np.array([clusterids[i+1]-clusterids[i]!=0 for i in range(n-1)],dtype=bool)
    b[1:-1]    = x[1:][uniqueids] - binbuffer
    b[-1]      = x[-1] + binbuffer
    return b                     

def getBinEdges4(x,nbin,binbuffer=0.001):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns bin edges (unsorted),
    by putting edges into the largest nbin gaps.
    Parameters
    ----------
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    """
    n    = len(x)
    assert n > nbin, "Number of bins should be larger than number of elements"
    bins = np.zeros(nbin+1)
    dx   = np.asarray([x[i+1]-x[i] for i in range(n-1)])
    sortids = np.argsort(-dx)
    bins[0] = x[0] - binbuffer
    for i in range(nbin-1):
        idx       = sortids[i]
        bins[i+1] = x[idx+1] - (dx[idx] * binbuffer)
    bins[nbin]    = x[-1] + binbuffer
    return bins

def getBinEdges5(x,nbin,ngap=1,binbuffer=0.001):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns bin edges (unsorted),
    by putting edges into the largest nbin gaps.
    Parameters
    ----------
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    """
    n    = len(x)
    assert n > nbin, "Number of bins should be larger than number of elements"
    bins = np.zeros(nbin+1)
    dx   = np.asarray([x[i+1]-x[i] for i in range(n-1)])
    sortids = np.argsort(-dx)
    bins[0] = x[0] - binbuffer
    for i in range(nbin-1):
        idx       = sortids[i]
        bins[i+1] = x[idx+1] - (dx[idx] * binbuffer)
    bins[nbin]    = x[-1] + binbuffer
    return bins
    
def getBinEdges(x, nbin,bintype=2,binbuffer=0.001,rangebuffer=0.1,rangetype=0,A=None,interval=[0]):
    """
    Given an array of numbers (x) and number
    of bins (nbins), returns bin edges,
    based on binning algortithm.
    bintype = 0 :
        Fixed uniform width bins
    bintype = 1 :
        Bin edges are adjusted to contain uniform number of values.
    bintype = 2 :
        Bin edges are adjusted to minimize distance from left edge.
    bintype = 3 :
        Bin edges are adjusted based on k-means clustering.    
    Input:
    x       - numpy array (dtype='float64')
    nbin    - int
    Returns:
            - numpy array (dtype='float64', len = nbin+1)
    TODO:
    Bisection type algorithms can be used to obtain optimum bin edges.
    Binning score can be used for better optimization of bin edges
    """
    if len(interval)==2:
        a, b = interval[0], interval[1]
    else: 
        Print("A tuple or list of two values is required to define the interval")
        return interval 
    
    nx = len(x)
    if nx > 1:
        dx   = x[1:] - x[:-1]
        Print("Min seperation of eigenvalues: {0:5.3e}".format(min(dx)))
        Print("Max seperation of eigenvalues: {0:5.3f}".format(max(dx)))
         
    if (nx < nbin or bintype == 0):
        Print("Uniform bins")
        bins = np.array([a,b])
    elif bintype == 1:
        Print("Adjust bin edges to have a uniform number of eigenvalues in each bin")
        bins = getBinEdges1(x,nbin)[0]   
    elif bintype == 2:
        Print("Adjust bin edges to minimize distance of values from the left edge of each bin")
        bins = getBinEdges2(x,nbin,binbuffer=binbuffer) 
    elif bintype == 3:
        Print("Adjust bin edges based on k-means clustering of eigenvalues")
        bins = getBinEdges3(x,nbin,binbuffer=binbuffer)  
                            
    if rangetype == 0:
        Print("Interval is set to: {0:5.3f}, {1:5.3f}".format(a,b))
    elif rangetype == 1 and nx > 1:
        Print("Interval is set to min & max of prior evals: {0:5.3f},{1:5.3f}".format(a,b))
        a = x[0]  - rangebuffer
        b = x[-1] + rangebuffer
    elif rangetype == 2: 
        diag   = A.getDiagonal()
        a = diag.min()[1]  - rangebuffer
        b = diag.max()[1]  + rangebuffer
        Print("Interval based on min & max of F diagonal: {0:5.3f},{1:5.3f}".format(a,b))
    elif rangetype == 3:
        diag   = A.getDiagonal()
        a = getLowerBound(A)                                                                                                        
        b = diag.max()[1]      + rangebuffer 
        Print("Interval based on min eval & max F diagonal: {0:5.3f},{1:5.3f}".format(a,b)) 
    elif rangetype == 4:
        a = getLowerBound(A)  - rangebuffer
        b = getUpperBound(A)  + rangebuffer
        Print("Interval based on min & max evals: {0:5.3f},{1:5.3f}".format(a,b))    
    bins[0]  = a
    bins[-1] = b           
    return np.sort(bins)

def getBinningScore(b,x):
    """
    Returns a score (lower is better) for given
    bin_edges (b), and values (x)
    1) Find the eigenvalues within each slice
    Within a slice:
        2) Compute the sum of distances of eigenvalues from the closest 
           neigbor on the left.
        3) Add this sum to the distance of the leftmost eigenvalue from the 
           left boundary.
    Returns the max sum for each slice.
    """
    nbin   = len(b)-1
    scores = np.zeros(nbin)
    nempty = 0 
    for i in range(nbin):
        xloc=x[(x>b[i]) & (x<b[i+1])] #1
        if len(xloc) > 1:
            tmp = np.sum(xloc[1:]-xloc[:-1]) #2
            scores[i]= xloc[0]-b[i] + tmp #3
        else:
            nempty += 1
    return max(scores), nempty

def initializeLog(debug):
    import sys
    if debug: logLevel = logging.DEBUG
    else: logLevel = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logLevel)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logLevel)

    logging.debug("Start in debug mode:") 

def getArgs():
    import argparse
    parser = argparse.ArgumentParser(description=
    """
    Aug 24, 2016
    Murat Keceli
    This code parses siesta-qetsc log files, log.*. 
    """
    )
    parser.add_argument('input', metavar='FILE', type=str, nargs='?',
        help='Log file to be parsed. All log files (any file with "log" in the filename) will be read if a log file is not specified.')
    parser.add_argument('-d', '--debug', action='store_true', help='Print debug information.')

    return parser.parse_args()  
          
def main():
    args=getArgs()
    initializeLog(args.debug)        
    if args.input is not None:
        logfile=args.input
        titers=getMaxIterTimes(logfile)
        tbins = getBinTimes(logfile)
        nbin   = getNumberofBins(logfile)
        niter  = getNumberofIters(logfile)
        bins  = getBins(logfile)
        evals = getEigenvalues(logfile)
        iterno = 6
        binno = 4
        print 'tbins:',tbins[iterno,:],titers[iterno]
        maxtbin = np.argmax(tbins[iterno,:])
        print 'nevals:',getNumberofEvalsPerBin(evals,bins)[iterno,:]
        print 'max bin:', maxtbin, bins[iterno,maxtbin],bins[iterno,maxtbin+1]
        print 'evals', evals[iterno,(evals[iterno,:]>bins[iterno,maxtbin]) & (evals[iterno,:]<bins[iterno,maxtbin+1])]
        print 'evals', getEvalsInBin(evals,bins,iterno,binno)
        maxt  = np.max(tbins[iterno,:])
        width = 0.1 + 0.2*tbins[iterno,:]/maxt
        print width
        plotEvalsAndBinsAndTimes(niter,evals,bins,tbins)
    else:
        readLogDirectory()
        

if __name__ == "__main__":
    main()
