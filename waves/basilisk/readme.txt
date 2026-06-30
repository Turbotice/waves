Par ex, ici chaque simulation ./bounce est lancé indépendamment et en parallèle, chacun sur 1 coeur.

Compiler un code basilisk :
qcc forced_jet_oscillo.c -lm

executer :
nohup ./a.out &

Le fichier 'maître' est le fichier bash loop-simu.sh, qui
1. crée un dossier par simu
2. met tout ce qu'il faut dedans (exécutable, fichier run.sh de paramètres ...).
3. Modifie le fichier 'run.sh' pour mettre les bons arguments puis l'exécute.

Le fichier bash run.sh lance une simu sur 1 coeur. Pour que chaque simu soit lancée sur plusieurs coeurs, il faut avoir précompilé le code en parallèle, puis il faut simplement remplacer ./mon_code $param1 $param2 par "mpirun -np 4 ./mon_code $param1 $param2" dans le fichier run.sh

Tout ceci se lance dans le terminal en faisant :
bash loop-simu.sh