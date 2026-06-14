import subprocess
import os

ipadour = "172.28.176.38"
iplaita = "172.28.159.188"
folder = '/media/turbots/DATA1/Jet_Surface/Basilisk/Forced/'#outputs/'

filelist = glob.glob('*/moments.h5')
print(filelist)

datafolder = folder + 'outputs'
if not os.path.exists(datafolder):
    os.makedirs(datafolder)

for filename in filelist:
    newname = filename.split('/')[-2]+'_'+os.path.basename(filename)
    subprocess.run(['cp',filename,f"{datafolder}/{newname}"])


if not os.path.exists('outputs'):
    os.makedirs('outputs')

subprocess.run(["scp",f"{datafolder}/*",f"stephane@{iplaita}:/outputs/"])
