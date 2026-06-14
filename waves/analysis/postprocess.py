import numpy as np
import glob
import os

import platform
import socket

global osname,ostype
ostype = platform.platform().split('-')[0]
osname = socket.gethostname()

from pprint import pprint


# detect all .txt files to process
# load each data set
# compute the averaged quantities
    # U_i^n, i in {x,y}, n in {0,1,2} for the velocity field
    # f^n n in {0,1,2} for surface
# compute the COD
# save the results in dictionnary formats ?
#keys must contain :
    #L, h0, U0, A0, f0

# display summary of the simulation
    # amplitude vs time
    # spatio temporal map
    # amplitude of the jet oscillation
    # amplitude of the surface oscillation

import waves.analysis.moments as moments
import waves.tools.rw_data as rw

import argparse

def gen_parser():    
    parser = argparse.ArgumentParser(description="Postprocess DNS of jet - Surface oscillation ")
    parser.add_argument('-ow', dest='overwrite', type=bool,default=False,help='overwrite previous .h5 file')
    parser.add_argument('-folder', dest='folder', type=str,default=None,help='To select a specific folder')
    parser.add_argument('-n', dest='n', type=int,default=None,help='To select the number of files to process')
    parser.add_argument('-t', dest='test', type=bool,default=True,help='To process only part of the files')

    #parser.add_argument('-step', dest='step', type=int,default=3,help='select Step to be performed')
#    print(parser)   
    args = parser.parse_args()
    print(args)
    return args

def sort_files(filelist):
    times = []
    newlist = []
    for filename in filelist:
        try:
            i = int(os.path.basename(filename).split('-')[1].split('.txt')[0])
            times.append(i)
            newlist.append(filename)
        except:
            print(f'cannot parse name, skip {filename}')
#    print(times)
    indices = np.argsort(times)
    filelist = np.asarray(newlist)[indices]
    return filelist

def load_resfile(filename,keys=['x','y','ux','uy','p','f','s']):
    #default keys values
    try:
        data = np.asarray(rw.read_csv(filename,delimiter=' '))[:,:-1].astype(float)
    except:
        print(f'Cannot read {filename}, skip')
        return None
    ns,nd = data.shape
    nx = 2**int(np.log2(ns)/2)
    ny = nx
    #print(nx,ny)
    data = np.reshape(data,(nx,ny,nd))

    d = {}
    for j,key in enumerate(keys):
        d[key] = data[...,j]
    return d

def get_params(filename):
    folder = os.path.dirname(filename)
    print(folder)
    fileparam = folder+'/params.txt'
    if os.path.exists(fileparam):
        raw = rw.read_csv(fileparam,delimiter='\t')
        d={}
        for line in raw:
            d[line[0]]=float(line[1])
        #print(d)
        return d
    else:
        print("fileparam is missing, skipping !")
        return None

def retrieve_parameters(folder,file='folder'):
    if file=='folder':
        names = folder.split('/')[-1].split('_')
    else:
        names = os.path.basename(folder).split('_')

    params = {}
    params['U0'] = float(names[2]+'.'+names[3])
    params['f0'] = float(names[6].replace('p','.')[1:])
    params['A0'] = float(names[8].replace('m',''))
    return params
        
def compute_moments(folder,params=None,overwrite=False,test=False,n=300):
    if folder is None:
        #use an example folder
        folder = '/Users/stephane/Documents/git/Notebooks/Jet_Surface/Data/256_U_0_4_forced/'
        
    filelist = glob.glob(folder+'/res-*.txt')
    #pprint(filelist)

    filelist = sort_files(filelist)
    if test:
        nmax = np.min([n,len(filelist)])
        filelist = filelist[:nmax]

    p = get_params(folder+'/')
    if p is not None:
        params.update(p)
    else:
        print('no parameter file detected, using generic one')

    filesave = folder+'/moments.h5'    
    if os.path.exists(filesave) and overwrite==False:
        return None

    data = {}
    for i,filename in enumerate(filelist):
        d = load_resfile(filename)
        if d is None:
            continue
        
        print(filename)
        d.update(params)
        
        Mx,My = moments.M_xy(d)
        Mf = moments.M_f(d)
        M = moments.variables(Mx,My,Mf=Mf)
        #M.update(params)
        #d.update(M)

        #print(M['eta'])
        for key in M.keys():
            if i==0:
                data[key]=[M[key]]
            else:
                data[key].append(M[key])

    data.update(params)
    #filename = filename.split('.txt')[0]+'.h5'
    rw.write_h5(filesave,data)

def scan(basefolder,test=False,overwrite=False,n=300):
    folders = glob.glob(basefolder+'*forced_w0_n*')
    print(folders)
    params = get_params(basefolder)
    if params is None:
        params = {}
        
    for folder in folders:
        print(folder)
        p = get_params(folder+'/')
        if p is not None:
            params=p

        params.update(retrieve_parameters(folder))
        compute_moments(folder,params=params,test=test,overwrite=overwrite,n=n)
        
def main(args):
    if 'macOS' in ostype:
        basefolder = '/Users/stephane/Documents/git/Notebooks/Jet_Surface/Data/'
    else:
        basefolder = '/media/turbots/DATA1/Jet_Surface/Basilisk/Forced/'
    if args.folder is not None:
        compute_moments(args.folder,params=None,overwrite=args.overwrite,test=args.test,n=args.n)
    else:
        folders = scan(basefolder,test=args.test,overwrite=args.overwrite,n=args.n)

if __name__ == '__main__':
    args = gen_parser()
    main(args)
