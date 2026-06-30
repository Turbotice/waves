#include "navier-stokes/centered.h"
#include "two-phase.h" 
#include "navier-stokes/conserving.h"
#include "tension.h"
#include "reduced.h"
#include "tracer.h"
#include "diffusion.h"

//Fluide 1 en bas, fluide 2 en haut

#define mu_1 0.1//1e-3 // (Pa.s)
#define mu_2 0.01*mu_1//1.85e-5
#define rho_1 1000. //(kg/m3)
#define rho_2 1.29 //(kg/m3)
#define nu_1 (mu_1/rho_1)
#define nu_2 (mu_2/rho_2)
#define sigma12 0.072
#define g 9.81

#define kappa_1 1e-7 //diffusivité thermique eau (m2/s)
#define kappa_2 2.24e-5 //diffusivité thermique air (m2/s)
#define beta_1 2e-4 //dilatation thermique (K^{-1})
#define beta_2 3e-3

#define L_physique 0.4 // length of the box (m)
#define h_physique 0.382*L_physique //hauteur du fluide 1
#define rayon_physique 0.02 //rayon panache thermique

//grandeurs adimensionnées
#define L (L_physique/L_physique) //length of the box
#define R (rayon_physique/L_physique) //rayon du jet ou panache
#define h (h_physique/L_physique) //hauteur de l'interface

#define Thaut_physique 270. // (K)
#define Tbas_physique 300.
#define Delta_T (Tbas_physique-Thaut_physique)
#define Thaut_adim 0.0 //adim
#define Tbas_adim (beta_1*Delta_T)


#define Pr_1 (nu_1/kappa_1)
#define Pr_2 (Pr_1*(kappa_1/kappa_2))

#define Gr_1 (g*pow(h_physique,3))/(pow(nu_1,2))
#define Gr_2 (Gr_1*((beta_2*rho_2)/(beta_1*rho_1)))

#define rho1_adim 1.
#define rho2_adim (rho_2/rho_1)
#define mu1_adim 1.
#define mu2_adim (mu_2/mu_1)

#define We ((rho_1*pow(nu_1,2))/(sigma12*L_physique))

#define Ra_1 (Gr_1*Pr_1*beta_1*Delta_T)

#define Pr(f) (clamp(f,0.,1.)*(Pr_1 - Pr_2) + Pr_2)
#define Gr(f) (clamp(f,0.,1.)*(Gr_1 - Gr_2) + Gr_2)

#define SIGMA12 (1./We)

double tmax = 10.;
double t_period = 1e-2;

scalar s[],T[];
scalar * tracers = {s,T};

face vector av[];

FILE * fpmax;

int main() {

  DT = 0.01; //pas max temporel

  rho1 = rho1_adim;
  rho2 = rho2_adim;
  mu1 = mu1_adim;
  mu2 = mu2_adim;
  L0 = L;
  a = av;

  TOLERANCE = 1e-2 [*];
  
  T[left] = neumann(0.);
  T[right] = neumann(0.);
  T[bottom] =(x > -R && x <R) ? dirichlet(Tbas_adim) : neumann(0.);
  //T[bottom] = dirichlet(Tbas_adim); //pour rayleih-bénard
  T[top] = dirichlet(Thaut_adim);

  u.n[top] = dirichlet(0.);
  u.n[bottom] = dirichlet(0.);
  u.n[right] = dirichlet(0.);
  u.n[left] = dirichlet(0.);
  u.t[top] = dirichlet(0.);
  u.t[bottom] = dirichlet(0.);
  u.t[right] = dirichlet(0.);
  u.t[left] = dirichlet(0.);

  N=128;
  origin (-L0/2., 0.);
  init_grid(N);
  periodic (right);

  char param_dim[80];
  sprintf (param_dim, "param_dim5.txt");
  FILE * fparam = fopen(param_dim, "w");
  fprintf (fparam, "L=%g h=%g R=%g Delta_T=%g\n rho_1=%g rho_2=%g mu_1=%g mu_2=%g kappa_1=%g kappa_2=%g beta_1=%g beta_2=%g\n N=%d t_period=%g tmax=%g\n"
    ,L_physique,h_physique,rayon_physique,Delta_T,rho_1,rho_2,mu_1,mu_2,kappa_1,kappa_2,beta_1,beta_2,N,t_period,tmax);
  fclose (fparam);

  char param2_adim[80];
  sprintf (param2_adim, "param_adim5.txt");
  FILE * fparam2 = fopen(param2_adim, "w");
  fprintf (fparam2, "L_adim=%g R_adim=%g h_adim=%g rho1_adim=%g rho2_adim=%g mu1_adim=%g mu2_adim=%g\n Pr_1=%g Pr_2=%g Gr_1=%g Gr_2=%g We=%g Ra=%g"
    ,L,R,h,rho1_adim,rho2_adim,mu1_adim,mu2_adim,Pr_1,Pr_2,Gr_1,Gr_2,We,Ra_1);
  fclose (fparam2);

  fpmax =  fopen("log.dat", "w"); 

  f.sigma = SIGMA12; //tension de surface

  run();
}

event init (t = 0) {
  system("rm frameGr5/temperatureGr5/*.*");
  system("rm interface/*.*");
  system("rm res/*.*"); 
  fraction(f, h-y);
  foreach() {
    u.x[] = 0.;
    T[] = Thaut_adim; //temperature linéaire cf loi de fick
  }
  boundary({T,u});
  foreach_face(){
    uf.x[] = 0.;
  }
  boundary ({f,u});
}

// event output (t += 0.1; t <= tmax){
//   static FILE * fp = fopen("interface.txt", "w");
//   fprintf(fp, "TIME %.6f\n", t);
//   output_facets(f, fp);
//   fprintf(fp, "\n");
//   fflush(fp);
// }


face vector D[];
event tracer_diffusion (i++) {
  foreach_face(){
    //D.x[] = (f[]*(1./Pr_w) + (1. - f[])*(1./Pr_g))*fm.x[];
    D.x[] = (1./Pr(f[]))*fm.x[];
  }
  diffusion (T, dt, D);
}

//ajout du terme de force volumique dépendant de T (et alpha en K^-1)
event acceleration (i++) {
	foreach_face(y){
		//av.y[] += (Gr_w*f[] + (1. - f[])*Gr_g)*(T[] + T[0,-1])/2.;
    av.y[] += (Gr(f[]))*(T[] + T[0,-1])/2.;
  }
}

event logfile (i++) {
  fprintf (stderr, "%d %g \n", i, t);
  fprintf (fpmax, "%d %g \n", i, t);
}

int isave1 = 1;
event res_save (t += t_period; t <= tmax) //tout les "t+=...", il générère un vtk avec tout les champs. Le calcul s'arrête à "t<=..."
{
  char name[80];
  
  sprintf (name, "interface/interface-%d.txt", isave1);
  FILE * fpfacet = fopen(name, "w");
  output_facets (f, fpfacet);
  fclose(fpfacet);

  sprintf (name, "res/res-%d.txt", isave1);
  FILE * fpres = fopen(name, "w");
  foreach()
    fprintf (fpres, "%g %g %g %g %g %g %g \n", x, y, u.x[], u.y[], p[],f[],T[]);
  fclose(fpres);
  
  isave1++;
}

char name[80];
char title[80];
int count = 0;
event movie (t = 0; t += t_period; t <= tmax) {

  clear();
  view (ty=-0.5, width = 1100, height = 1100);
  squares("T", linear=true, map=jet, cbar=true, min=Thaut_adim, max=Tbas_adim);
  draw_vof ("f", lw = 2); //gère l'interface grâce à f : quel fluide est où
  //sprintf (name, "frameGr4/temperatureGr4/T-%06d.png", i);
  //labels("f");
  sprintf(title, "t=%.2f s", count*t);
  draw_string(title, pos=1);
  sprintf(name, "frameGr5/temperatureGr5/T-%06d.png", count);
  save(name);

  // clear();
  // view (ty=-0.5, width = 1100, height = 1100);
  // squares ("f", spread = -1,
  //   cbar = true, border = true, pos = {0.5,  0.0},
  //   label = "f", mid = true, format = "%9.5f", levels = 10);
  // draw_vof ("f",filled=1, fc = {0.,0.8,0.8}, lw = 2);
  // draw_vof ("f",filled=-1, fc = {1.,0.,0.}, lw = 2);
  // sprintf (name, "frameGr4/fGr4/snapshot-%06d.png", (int) round(t*1000));
  // save(name);

  // clear();
  // view (ty=-0.5, width = 1100, height = 800);
  // scalar omega[];
  // vorticity (u, omega);
  // // squares ("omega", spread = -1,
  // //    cbar = true, border = true, pos = {0.5,  0.0},
  // //    label = "omega", mid = true, format = "%9.5f", levels = 10);
  // squares("omega", spread=-1, linear=true, map=jet, cbar=true);
  // draw_vof ("f", lw = 2);
  // sprintf (name, "frame/vorticity/vort-%d.png", i);
  // save(name);
  count++;
}

event profile (t = end) {
  printf ("-----END-----\n");
}