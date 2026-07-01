/**
# Self-Induced Sloshing by a Jet
*/

#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#include "two-phase.h" 
#include "tension.h"
#include "navier-stokes/conserving.h"
#include "vtknew.h" //permets de générer des vtk pour visualiser les champs avec paraview
#include "tracer.h"
#include "tag.h"

//Paramètres simu.
double h;
double U0;
double R_d;

//Sauvegarde paramètres adim. et autres
double grav;
double t_period;
double t_max;

double Fr;
double Re;
double mu_b;
double rho_b;
double R_1;
double R_2;

/**
A passive tracer is injected with the jet to follow lagrangian paths.
*/

scalar s[];
scalar * tracers = {s};

FILE * fpmax; //

int main() {

  t_period=0.05;
  t_max=600;

  R_d=0.003; 
  L0=0.4; 
  rho2 = 1.3;
  rho1=1000;
  mu1 = 0.1;
  mu2 = 0.01*mu1;
  
  U0=0.775;
  
  h=0.15;
  grav=9.81;

  TOLERANCE = 1e-3 [*];

  u.n[bottom] = dirichlet (f[]*U0*(x > -R_d && x <R_d));
  u.t[bottom] = dirichlet(0.);

  u.n[top] = u.n[] > 0. ? neumann(0.) : dirichlet(0.);
  p[top] = dirichlet(0.);
  s[bottom] = dirichlet (f[]*U0*(x > -R_d && x <R_d));

  u.n[left] = y < R_d ? dirichlet(-U0) : dirichlet(0.);
  u.n[right] = y < R_d ? dirichlet(U0) : dirichlet(0.);
  u.t[left] = y < R_d ? neumann(0.) : dirichlet(0.);
  u.t[right] = y < R_d ? neumann(0.) : dirichlet(0.);
 
  N=512;
  origin (-L0/2, 0);
  init_grid(N);
  
  fpmax =  fopen("log.dat", "w");

  char param_dim[80];
  sprintf (param_dim, "param_dim.txt");
  FILE * fparam = fopen(param_dim, "w");
  fprintf (fparam, "%g %g %g %g %g %g %g %g %d %g %g\n",L0,h,R_d,U0,rho1,rho2,mu1,mu2,N,t_period,t_max);
  fclose (fparam);
  
  f.sigma = 0.072;

  run();
}

/**
We initiate gravity, which is opposing to the inertia of the jet.
*/

event init (t = 0) {

  if (!restore("restart")) {
    fprintf(stderr, "Starting new simulation.\n");
  } else {
    fprintf(stderr, "Restarting from previous dump\n");
  }

  Re=rho1*U0*R_d/mu1;
  Fr=U0/sqrt(grav*h);
  mu_b=mu2/mu1;
  rho_b=rho2/rho1;
  R_1=R_d/L0;
  R_2=h/L0;

  char dim_adim[80];
  sprintf (dim_adim, "dim_adim.txt");
  FILE * fparam = fopen(dim_adim, "w");
  fprintf (fparam, "%g %g %g %g %g %g\n",Re,Fr,mu_b,rho_b,R_1,R_2);
  fclose (fparam);

  fraction (f, y<h);
}

#if 1
event acceleration (i++) {
  face vector av = a;
  foreach_face(y)
    av.y[] = -9.81;
}
#endif

event logfile (i++) {
  fprintf (stderr, "%d %g \n", i, t);
  fprintf (fpmax, "%d %g \n", i, t);
}

/**
We kill eventual numerical bubbles that are under a critical size
*/

event remove_droplets (i++) {
  remove_droplets (f, threshold=0.05, bubbles=true);
}

/**
We save interfaces for complex orthogonal decomposition (to find the sloshing modes). We can also track at each height $y$ the maximum of $|\underline{u}|$ and have the "position" of the jet through time, and apply the same post-treatment.
*/

int isave1 = 1;
event res_save (t += 0.05; t <= 600) //tout les "t+=...", il générère un vtk avec tout les champs. Le calcul s'arrête à "t<=..."
{
  char name[80];
  
  sprintf (name, "interface-%d.txt", isave1);
  FILE * fpfacet = fopen(name, "w");
  output_facets (f, fpfacet);
  fclose(fpfacet);

   sprintf (name, "res-%d.txt", isave1);
  FILE * fpres = fopen(name, "w");
  foreach()
    fprintf (fpres, "%g %g %g %g %g \n", x, y, u.x[], u.y[], p[]); //f[],s[]);
  fclose(fpfacet);
  
  isave1++;
}

/**
To visualize both the surface and the jet, we can follow lagrangian trajectories using a passive tracer. We generate videos:
*/
event ppm_output (t = 0; t += 0.05; t <= 600){
  char name[80];
  sprintf (name, "f.mp4");
  output_ppm (f, file = name, n = 512, min = 0, max = 1, linear = true);
  
  char name0[80];
  sprintf (name0, "uX.mp4");
  output_ppm (u.x, file = name0, n = 512, min = -U0, max = +U0, linear = true);

  char name1[80];
  sprintf (name1, "uY.mp4");
  output_ppm (u.y, file = name1, n = 512, min = -U0, max = +U0, linear = true);

  // optionally tracer
  char name2[80];
  sprintf (name2, "s.mp4");
  output_ppm (s, file = name2, n = 512, min = 0., max = U0, linear = true);
}

/*
int ivtk2 = 1;
event movies (t += 0.1; t <= 80) //tout les "t+=...", il générère un vtk avec tout les champs. Le calcul s'arrête à "t<=..."
{
  scalar omega[];
  vorticity (u, omega);

  char name[80];
  sprintf (name, "snapshot-%d.vtk", ivtk2);
  FILE * fpvtk = fopen(name, "w");
  output_vtk ({omega,u.x,u.y,p,f,s}, fpvtk);
  fclose(fpvtk);

  ivtk2++;
}
*/

double t_prev_dump = 0.;

event dump_state (t = 0; t += 10; t <= 600) //t_max
{ 
  dump("restart");
  t_prev_dump = t;
  fprintf(stderr, "Dumped state at t = %g\n", t);

  char name[80];
  sprintf(name, "res_t%.1f.txt", t);
  FILE * fpres = fopen(name, "w");
  foreach()
    fprintf(fpres, "%g %g %g %g %g %g \n", x, y, u.x[], u.y[], p[], s[]);
  fclose(fpres);
}

event profile (t = end) {
  printf ("-----END-----\n");
}
