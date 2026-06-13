
#fig,ax = plt.subplots(figsize=(15,2))#,ncols=3)
import numpy as np

def surface_position(h,L,ny):
    # detect the surface position :
    jmax = int(np.round(ny*h/L))
    return jmax

def variables(Mx,My,Mf=None):
    M={}
    #print(Mx[1])
    M['Q_x'] = Mx[0]
    M['zeta'] = Mx[1]/Mx[0]
    M['sigma_z'] = Mx[2]/Mx[0]-M['zeta']**2#check !!!
    
    if Mf is not None:
        M['eta'] = Mf[0]
        
    return M

def moment_u(x,u,param):
    [nx,ny] = u.shape
    
    imin = int(np.round(nx/4))
    imax = int(np.round(3*nx/4))
    jmax = surface_position(param['h'],param['L'],ny)

    x = x[imin:imax,:jmax]
    Z = u[imin:imax,:jmax]

    M={}
    for n in range(3):
        M[n]= np.sum(x**n*Z,axis=0)
    return M
                
def M_xy(d):
    Mx = moment_u(d['x'],d['ux'],d)
    My = moment_u(d['x'],d['uy'],d)
    return Mx,My

def M_f(d):
    Mf = moment_u(d['y'],d['f'],d)
    return Mf
