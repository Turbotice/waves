import subprocess
import os
import glob

ipadour = "172.28.176.38"
iplaita = "172.28.159.188"
folder = '/media/turbots/DATA1/Jet_Surface/Basilisk/Forced/'#outputs/'

filelist = glob.glob('*/moments.h5')
print(filelist)

if not os.path.exists('outputs'):
    os.makedirs('outputs')

subprocess.run(["scp",f"turbots@{ipadour}:{folder}outputs/*",'outputs/'])
