import subprocess
import os
import glob
from pprint import pprint

folder = '/media/turbots/DATA1/Jet_Surface/Basilisk/Forced/'#outputs/'

filelist = glob.glob(folder+'*/moments.h5')
pprint(filelist)

datafolder = folder + 'outputs'
if not os.path.exists(datafolder):
    os.makedirs(datafolder)

for filename in filelist:
    newname = filename.split('/')[-2]+'_'+os.path.basename(filename)
    subprocess.run(['cp',filename,f"{datafolder}/{newname}"])
