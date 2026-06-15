import subprocess
import os
import glob
import argparse

def gen_parser():    
    parser = argparse.ArgumentParser(description="Compile .h5 files in one folder")
    parser.add_argument('-ow', dest='overwrite', type=bool,default=True,help='overwrite previous .h5 file')
    parser.add_argument('-f', dest='folder', type=str,default="",help='To target a specific folder')

    #parser.add_argument('-step', dest='step', type=int,default=3,help='select Step to be performed')
#    print(parser)   
    args = parser.parse_args()
    print(args)
    return args


def main(folder):
    ipadour = "172.28.176.38"
    iplaita = "172.28.159.188"
    folder = '/media/turbots/DATA1/Jet_Surface/Basilisk/'+folder+'/'#outputs/'

    filelist = glob.glob('*/moments.h5')
    print(filelist)

    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    subprocess.run(["scp",f"turbots@{ipadour}:{folder}outputs/*",'outputs/'])

if __name__ == '__main__':
    args = gen_parser()
    main(args.folder)
