import subprocess
import os
import glob
from pprint import pprint
import argparse
#base folder
global basefolder
basefolder = '/media/turbots/DATA1/Jet_Surface/Basilisk/'#outputs/'

def gen_parser():    
    parser = argparse.ArgumentParser(description="Compile .h5 files in one folder")
    parser.add_argument('-ow', dest='overwrite', type=bool,default=True,help='overwrite previous .h5 file')
    parser.add_argument('-f', dest='folder', type=str,default="",help='To target a specific folder')

    #parser.add_argument('-step', dest='step', type=int,default=3,help='select Step to be performed')
#    print(parser)   
    args = parser.parse_args()
    print(args)
    return args

def main(f):
    folder = basefolder+f
    filelist = glob.glob(folder+'/*/moments.h5')
    pprint(filelist)

    datafolder = folder + '/outputs'
    if not os.path.exists(datafolder):
        os.makedirs(datafolder)

    for filename in filelist:
        newfolder = f+'_'+filename.split('/')[-2]+'_'
        newname = newfolder.replace('.','_') + os.path.basename(filename)
        subprocess.run(['cp',filename,f"{datafolder}/{newname}"])

if __name__ == '__main__':
    args = gen_parser()
    main(args.folder)
