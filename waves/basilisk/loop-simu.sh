#!/bin/bash

# Values to test

Bo=0.2649183
Oh=0.1616947
OMEGA=1
LEVEL=8
Nperiod=2048

Gamma=(1.8315 1.832 1.834 1.835)
phase=(0 0.5 1 1.5)

# Original files
RUN_TEMPLATE="run.sh"
CODE_EXEC="./bounce_coherent"

# Loop over all combinations
for p1 in "${Gamma[@]}"; do
    for p2 in "${phase[@]}"; do

        # Folder name
        dirname="bounce_Bo${Bo}_Oh${Oh}_OMEGA${OMEGA}_phi${p2}_GAMM${p1}"

        echo "Creating ${dirname}"

        # Create directory
        mkdir -p "$dirname"

        # Copy files
        cp "$RUN_TEMPLATE" "$dirname/"
        cp "$CODE_EXEC" "$dirname/"

        # Modify parameters inside run.sh
        sed -i "s/^GAMMA=.*/GAMMA=${p1}/" "$dirname/run.sh"
        sed -i "s/^phase=.*/phase=${p2}/" "$dirname/run.sh"
        sed -i "s/^Nperiod=.*/Nperiod=${Nperiod}/" "$dirname/run.sh"

        # Go into directory and run
        (
            cd "$dirname" || exit
            chmod +x $RUN_TEMPLATE
            nohup ./$RUN_TEMPLATE > output.log 2>&1 &
        )

    done
done
