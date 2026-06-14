#!/bin/bash

# Values to test

freq=(0.825 0.86 0.87 0.88 0.89 0.91 0.92 0.93 0.94 0.96 0.97 0.98 0.99 1.01 1.02 1.03 1.04 1.06 1.08 1.15)

# Original files
RUN_TEMPLATE="run.sh"
CODE_EXEC="./forced_jet_oscillo"

# Loop over all combinations
for p1 in "${freq[@]}"; do
        # Folder name
        dirname="256_U_0_4_forced_w0_n${freq}_A_50m"

        echo "Creating ${dirname}"

        # Create directory
        mkdir -p "$dirname"

        # Copy files
        cp "$RUN_TEMPLATE" "$dirname/"
        cp "$CODE_EXEC" "$dirname/"

        # Modify parameters inside run.sh
        sed -i "s/^freq=.*/freq=${p1}/" "$dirname/run.sh"

        # Go into directory and run
        (
            cd "$dirname" || exit
            chmod +x $RUN_TEMPLATE
            nohup ./$RUN_TEMPLATE > output.log 2>&1 &
        )
done
