import numpy as np
from numpy import pi as pi

## Physical parameters
global g
g = 9.81


def fsurface(L,h0,m=1):
    k = m*pi/L
    return 1/(2*pi)*(g*k*np.tanh(k*h0))**(1/2)

def fjet(L,h0,n=1):
    if type(L) is float:
        L = np.asarray(L)
    return 1/(2*pi)*(n*g/h0)**(1/2)*np.ones(L.shape)

def deltaf(L,h0,m=1,n=1):
    fs = fsurface(L,h0,m=m)
    fj = fjet(L,h0,n=n)
    return fj-fs

def deltaf_norm(L,h0,m=1,n=1):
    fs = fsurface(L,h0,m=m)
    fj = fjet(L,h0,n=n)
    return 2*(fj-fs)/(fj+fs)
    
def confusion(x,m=1,n=1):
    return x*np.tanh(m*x)-n/m

def eigens(p,a=1):
    mat_4=np.array([[0, 1, 0, 0],
                    [-p['omega_1']**2, -p['lambda_1'], a*p['a_1'], 0],
                    [0, 0, 0, 1],
                    [-a*p['a_2'], 0, -p['omega_2']**2, -p['lambda_2']]])
    lamb,v=np.linalg.eig(mat_4)
    idx = np.argsort(lamb.real)[::-1]   
    lamb = lamb[idx]
    return lamb

def growth_rate(p,a=1):
    lamb = eigens(p,a=a)
    return np.real(lamb[0])

def frequency(p,a=1):
    lamb = eigens(p,a=a)
    return np.abs(np.imag(lamb[0]))
    
def find_threshold(p):
    ac = sp.optimize.brentq(lambda a:growth_rate(p,a=a),0,10**6)
    return ac
