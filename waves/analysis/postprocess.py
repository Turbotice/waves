import numpy as np
import glob
import os

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

def sort_files(filelist):
    times = [int(os.path.basename(filename).split('-')[1].split('.txt')[0]) for filename in filelist]
#    print(times)
    indices = np.argsort(times)
    filelist = np.asarray(filelist)[indices]
    return filelist

def load_resfile(filename,keys=['x','y','ux','uy','p','f','s']):
    #default keys values
    data = np.asarray(rw.read_csv(filename,delimiter=' '))[:,:-1].astype(float)
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

def scan(basefolder):
    folders = glob.glob(basefolder+'*forced_w0_n*')
    print(folders)
    params = get_params(basefolder)
    for folder in folders:
        print(folder)
        names = folder.split('/')[-1].split('_')
        params['U0'] = float(names[2]+'.'+names[3])
        params['w0'] = float(names[6].replace('p','.')[1:])
        params['A0'] = float(names[8].replace('m',''))
        
        compute_moments(folder,params=params)
        
def compute_moments(folder,params=None):
    if folder is None:
        #use an example folder
        folder = '/Users/stephane/Documents/git/Notebooks/Jet_Surface/Data/256_U_0_4_forced/'
        
    filelist = glob.glob(folder+'res*.txt')
    filelist = sort_files(filelist)
    pprint(filelist)

    p = get_params(filename)
    if p is not None:
        params=p
    else:
        print('no parameter file detected, using generic one')
            
    data = {}
    for i,filename in enumerate(filelist):
        d = load_resfile(filename)

        d.update(params)
        
        Mx,My = moments.M_xy(d)
        Mf = moments.M_f(d)
        M = moments.variables(Mx,My,Mf=Mf)
        #M.update(params)
        #d.update(M)

        for key in M.keys():
            if i==0:
                data[key]=[M[key]]
            else:
                data[key].append(M[key])

    data.update(params)
    filesave = os.path.dirname(filename)+'/moments.h5'    
    #filename = filename.split('.txt')[0]+'.h5'
    rw.write_h5(filesave,data)

def main():
    basefolder = '/Users/stephane/Documents/git/Notebooks/Jet_Surface/Data/'
    basefolder = '/media/turbots/DATA1/Jet_Surface/Basilisk/Forced/'
    folders = scan(basefolder)

main()
