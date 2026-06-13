import waves.display.graphes as graphes
import waves.tools.rw_data as rw

from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib

def plot_fields():
    fig,axs = plt.subplots(figsize=(12,10),ncols=2,nrows=2)

    sc = axs[0,0].pcolormesh(x,y,ux)
    plt.colorbar(sc)
    graphes.legende('','',r'$u_x$',ax = axs[0,0])
    sc = axs[0,1].pcolormesh(x,y,uy)
    graphes.legende('','',r'$u_y$', ax = axs[0,1])
    axs[0,1].contour(x,y,uy,10,alpha=1,colors='w')
    plt.colorbar(sc)
    #[X,Y] = np.meshgrid(x,y)

    rho = 1000
    g = 9.81
    dpx = np.gradient(p)[0]
    sc = axs[1,1].pcolormesh(x,y,dpx,vmin=-0.2,vmax=0.2)

    contours = np.linspace(-0.2,-0.1,5)
    axs[1,1].contour(x,y,dpx,contours,alpha=1,colors='w')
    contours = np.linspace(0.1,0.2,5)
    axs[1,1].contour(x,y,dpx,contours,alpha=1,colors='w')

    graphes.legende('','',r'$\partial_x p$',ax = axs[1,1])

    plt.colorbar(sc)

    p0 = -9759.18447655
    ys = y-0.15
    pd = (p-p0*ys)*(ys<0)
    sc = axs[1,0].pcolormesh(x,y,pd,vmin=-5,vmax=10)
    axs[1,0].contour(x,y,pd,100,alpha=1,colors='w')

    figs = graphes.legende('','',r'$p$',cplot=True,ax = axs[1,0])


    #graphes.save_figs(figs,savedir=savefolder,prefix='Field_Simu_')
    #sc = axs[1,0].pcolormesh(x,y,np.gradient(p)[0],vmin=-0.2,vmax=0.2)
    #axs[1,0].axis([-0.2,0.2,0.14,0.16])
    plt.colorbar(sc)


def contours():
    fig,ax = plt.subplots(figsize=(12,10*0.38))#,ncols=2,nrows=2)

    p0 = -9759.18447655
    ys = y-0.15
    pd = (p-p0*ys)*(ys<0)
    x1 = np.linspace(min(x[:,0]),max(x[:,0]),len(x[:,0]))
    y1 = np.linspace(min(y[0,:]),max(y[0,:]),len(y[0,:]))

    sc = ax.streamplot(x1,y1,np.transpose(ux),np.transpose(uy),density=3)#,vmin=-5,vmax=10)
    #ax.contour(x,y,pd,200,alpha=1,colors='w')

    plt.axis([-0.2,0.2,0,0.15])
    figs = graphes.legende('$x$','$y$',r'$\vec u$',cplot=True,ax = ax)


    #graphes.save_figs(figs,savedir=savefolder,prefix='Field_Velocity_',frmt='png')
    #sc = axs[1,0].pcolormesh(x,y,np.gradient(p)[0],vmin=-0.2,vmax=0.2)
    #axs[1,0].axis([-0.2,0.2,0.14,0.16])
    #plt.colorbar(sc)
