# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 09:42:14 2026

@author: M3051168
"""

####################### COD for Basilisk ###################
# A savoir : ici je n'ai mis que les fonctions minimale, et elles
# sont en l'état. C'est important de bien regarder comment la COD
# fonctionne sur le GIT. Si il y a des choses bizarres au niveau des
# scalings, de comment les amplitudes sont calculés etc., c'est le GIT
# et le .pdf sur Arxiv la référence.
############################################################

# Packages standards

import scipy.fft as scifft
from scipy.stats import linregress
from scipy.signal import detrend, find_peaks
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from matplotlib.ticker import MaxNLocator
import csv

# Fonctions usuelles

def replace_nan(matrix):
    """interpolation des 'nan' dans les matrices"""
    ok = ~np.isnan(matrix)
    xp = ok.ravel().nonzero()[0]
    fp = matrix[~np.isnan(matrix)]
    x  = np.isnan(matrix).ravel().nonzero()[0]
    
    matrix[np.isnan(matrix)] = np.interp(x, xp, fp)
    return matrix

############################################################

# Calling the data 

data_dir='./test_stage/'

# Surface

nt=400
nx=256
delta_t=1/20 #1/fps
T_vid=20
list_t=np.linspace(0,T_vid,400)

sig_surf=np.zeros((nt,nx)) #Signal_surface

with open(data_dir+'pos_surf.csv', encoding='utf8') as File:
    reader = csv.reader(File, delimiter=';')
    data_list = list(reader)
    i=0
    for line in data_list[0:]:
            sig_surf[i][:]=line
            i=i+1
        
File.close()

list_x_surf=[]

with open(data_dir+'abscisse_surf.csv', encoding='utf8') as File:
    reader = csv.reader(File, delimiter=';')
    data_list = list(reader)
    for line in data_list[0:]:
        list_x_surf.append(float(line[0]))
        
File.close()

#On sait jamais

if len(list_x_surf)!=len(sig_surf[0]):
    list_x_surf=np.linspace(-0.2,0.2,nx)

# Jet

nz=30

sig_jet=np.zeros((nt,nz)) #Signal_jet

with open(data_dir+'pos_jet.csv', encoding='utf8') as File:
    reader = csv.reader(File, delimiter=';')
    data_list = list(reader)
    i=0
    for line in data_list[0:]:
            sig_jet[i][:]=line
            i=i+1
        
File.close()

list_z_jet=[]

with open(data_dir+'ordonnee_jet.csv', encoding='utf8') as File:
    reader = csv.reader(File, delimiter=';')
    data_list = list(reader)
    for line in data_list[0:]:
        list_z_jet.append(float(line[0]))
        
File.close()

############################################################

# Fonctions COD (v. Basilisk)

def H_transform(sig_surf,sig_jet,nt,time_start=0,time_end=-1):
    """Extraction de la partie positive du spectre pour le jet et la surface + transformée inverse (Hilbert's transform). 
    Les sorties sont formatée pour l'utilisation de la décomposition complexe orthogonale"""
    
    # Jet
    ind_start=int(time_start*1/delta_t)
    if time_end==-1:
        sp_time_mat=replace_nan(sig_jet[ind_start:,:])
    else:
        ind_end=int(time_end*1/delta_t)
        sp_time_mat=replace_nan(sig_jet[ind_start:ind_end,:])
    
    fft_temp_prep_jet=np.zeros((nt,nz),dtype=complex)
      
    #sp_time_mat=sp_time_mat-np.mean(sp_time_mat,axis=0) 
    
    fft_temp=scifft.fftshift(scifft.fft(sp_time_mat, axis=0),axes=0)
    f_axis=np.linspace(-1/(2*delta_t),1/(2*delta_t),nt)

    fft_temp_prep_jet[int(len(f_axis)/2):][:]=fft_temp[int(len(f_axis)/2):][:]
    fft_temp_prep_jet[int(len(f_axis)/2)+1:][:]=2*fft_temp[int(len(f_axis)/2)+1:][:]

    mat_jet=scifft.ifft(fft_temp_prep_jet, axis=0)
    
    # Surface
    ind_start=int(time_start*1/delta_t)
    if time_end==-1:
        sp_time_mat=replace_nan(sig_surf[ind_start:,:])
    else:
        ind_end=int(time_end*1/delta_t)
        sp_time_mat=replace_nan(sig_surf[ind_start:ind_end,:])

    fft_temp_prep_surf=np.zeros((nt,nx),dtype=complex) 
    #sp_time_mat=sp_time_mat-np.mean(sp_time_mat,axis=0) 
    
    fft_temp=scifft.fftshift(scifft.fft(sp_time_mat, axis=0),axes=0)
    f_axis=np.linspace(-1/(2*delta_t),1/(2*delta_t),nt)

    fft_temp_prep_surf[int(len(f_axis)/2):][:]=fft_temp[int(len(f_axis)/2):][:]
    fft_temp_prep_surf[int(len(f_axis)/2)+1:][:]=2*fft_temp[int(len(f_axis)/2)+1:][:]

    mat_surf=scifft.ifft(fft_temp_prep_surf, axis=0)
    
    return mat_surf,mat_jet

def comp_ortho_dec(h_mat,plot=1):
    """Réalise l'opération de C.O.D. (décomposition orthogonale complexe)"""
    nt, n_space = h_mat.shape
    Z = h_mat.T
    R = (1 / nt) * Z @ Z.conj().T  # Matrice de covariance complexe hermitienne

    # Utiliser eigh pour une meilleure stabilité (car R est hermitienne)
    lamb, v = np.linalg.eigh(R)
    idx = lamb.argsort()[::-1]
    lamb = lamb[idx]
    v = v[:, idx]

    lamb = np.abs(np.real(lamb))  # Pour s'assurer que c'est bien réel et positif
    Q_d = v.conj().T @ Z  # Projection dans la base propre
    
    for i in range(n_space):
       q=Q_d[i,:]
       q_fixed = q.copy()
       q_fixed[1::2] *= -1
               
       Q_d[i,:]=q_fixed

    if plot==1:
        fig, ax = plt.subplots(dpi=500)
        ax.plot(lamb,'*')
        plt.xlabel('Component N°')
        plt.yscale('log')
        plt.ylabel('Energy of Components')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.grid()
        plt.title('Eigenvalues of C.O.D')
    
    return lamb, v, Q_d, max(lamb)

def make_1D_signal(v_surf,v_jet,Q_d_surf,Q_d_jet,n_mod):
    """Renvois les fonctions temporelles (jet et surface) de la C.O.D."""
    
    sig_t_surf_mod=max(np.abs(v_surf[:,n_mod]))*Q_d_surf[n_mod, :]
    sig_t_jet_mod=max(np.abs(v_jet[:,n_mod]))*Q_d_jet[n_mod, :]
 
    return sig_t_surf_mod,sig_t_jet_mod

def fourier_temps_COC(mat_coc,nt,lamb,v,n_mod):
    """Réalise la transformée de Fourier des "n_mod" composantes via les "Complex Ortho. Coor" de la décompo.
    orthogonale complexe. Cette fonction ne peut pas être appellée seule, il faut lui donner la 
    matrice de coordonnées complexes "mat_coc" ('Q_d' dans Feeny et al.) issus de la décomposition."""
        
    mat_coc=np.transpose(mat_coc)   
    (nt,n_m) = np.shape(mat_coc)
    
    #Fenetrage
    
    win = np.hamming(nt)
    mat_coc = mat_coc*win[None,:,None]
    
    #Transformation de Fourier temporelle
    
    fft_temp_mat=scifft.fft(mat_coc, axis=1)
    f_axis=np.linspace(0,1/(delta_t),nt)
    
    mat=np.abs(np.mean(fft_temp_mat,axis=0)) #(1,nt,1) -> (nt,1)

    fft_return=np.sqrt(np.pi)*max(np.abs(v[:,n_mod]))/len(f_axis)*np.abs(mat[:,n_mod])
      
    return [fft_return,f_axis]

def traveling_index(v):
    """Calcul l'inverse du condition number de la matrice reel/imag d'un vecteur"""
    """Cela permet de connaitre la composante propagative/stationnaire d'un signal
    complexe"""
    W=np.zeros((len(v),2))
    W[:,0]=np.real(v)
    W[:,1]=np.imag(v)
    
    alpha=1/np.linalg.cond(W)
    return alpha

def norm_mod(v):
    "Norme L2 sur l'espace des vecteurs propres issus de la décomposition orthogonale complexe"
    som=0
    for i in range(len(v)):
        som += np.abs(v[i])**2
    return np.sqrt(som)

############################################################

# Test + sorties usuelles

#Step 1 : Transformée de Hilbert
[mat_surf,mat_jet]=H_transform(sig_surf,sig_jet,nt,time_start=0,time_end=-1) #"complexifie" le signal

#Step 2 : COD (résolution pb valeur propre pour la matrice d'autocorrélation)
lamb_surf,v_surf,Q_d_surf,lamb_max=comp_ortho_dec(mat_surf,1)
lamb_jet,v_jet,Q_d_jet,lamb_max=comp_ortho_dec(mat_jet,1)

#Step 3 : Formes spatiales pour la composante n_mod 

n_mod=0 #première composante n_mod=0

#
plt.figure(dpi=500)
plt.title('Jet')
plt.plot(np.sqrt(lamb_jet[n_mod])*np.abs(v_jet[:,n_mod]),list_z_jet,'r')
plt.plot(-np.sqrt(lamb_jet[n_mod])*np.abs(v_jet[:,n_mod]),list_z_jet,'r')
plt.xlabel(r'$A_{jet}~[m]$')
plt.ylabel(r'$z [m]$')
plt.xlim([-0.21,0.21])
plt.ylim([0,0.2])
plt.grid('both')

plt.figure(dpi=500)
plt.title('Surface')
plt.plot(list_x_surf, np.sqrt(lamb_surf[n_mod])*np.abs(v_surf[:,n_mod]),'b')
plt.plot(list_x_surf,-np.sqrt(lamb_surf[n_mod])*np.abs(v_surf[:,n_mod]),'b')
plt.ylabel(r'$A_{surf}~[m]$')
plt.xlabel(r'$x [m]$')
plt.xlim([-0.21,0.21])
plt.ylim([0,0.2])
plt.grid('both')

#Step 4 : FFT de la fonction temporelle pour la composante n_mod 

#“Anyone who tries to analyse a time series without plotting it first is asking for trouble." Chris Chatfield, The Analysis of Time Series: An Introduction (1984)

#Signaux temporels

[sig_t_surf_mod,sig_t_jet_mod]=make_1D_signal(v_surf,v_jet,Q_d_surf,Q_d_jet,n_mod)

plt.figure(dpi=500)
plt.plot(list_t,sig_t_jet_mod,'r',label=r'$Z_0 c_0(t), ~\mathrm{Jet}$')
plt.xlabel(r't [s]')
plt.ylabel(r'Amplitude [m]')
plt.legend()

plt.figure(dpi=500)
plt.plot(list_t,sig_t_surf_mod,'b',label=r'$H_0 a_0(t),~\mathrm{Surface}$')
plt.xlabel(r't [s]')
plt.ylabel(r'Amplitude [m]')
plt.legend()

#FFTs

[fft_surf,f_axis]=fourier_temps_COC(Q_d_surf, nt, lamb_surf, v_surf, n_mod)
[fft_jet,f_axis]=fourier_temps_COC(Q_d_jet, nt, lamb_jet, v_jet, n_mod)

fig, ax = plt.subplots(dpi=500)
plt.xlabel(r'$f$ (Hz)')
plt.grid(which='both')             
plt.title(r'')
plt.xlim([0,10])
plt.ylabel(r'Amplitude (m)')
ax.plot(f_axis,fft_surf,'b', linewidth=0.5,label="Surface")
ax.plot(f_axis,fft_jet,'r', linewidth=0.5,label='Jet')
plt.legend()
plt.title('C.O.C. spectra surf for comp. n°={}'.format(n_mod+1))

# Travelling index

print('Travelling ind. surf :',traveling_index(v_surf[:,n_mod]))
print('Travelling ind. jet :',traveling_index(v_jet[:,n_mod]))





