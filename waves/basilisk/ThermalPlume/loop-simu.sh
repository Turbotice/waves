#!/bin/bash
# Values to test
DT=(1. 2. 5. 10. 20. 50. 100.)
# values to be at the resonance of jet oscillation, but not the surface
#freq=(0.825 0.86 0.87 0.88 0.89 0.91 0.92 0.93 0.94 0.96 0.97 0.98 0.99 1.01 1.02 1.03 1.04 1.06 1.08 1.15)
# Original files
RUN_TEMPLATE="run.sh"
CODE_EXEC="./a.out"
# Loop over all combinations
for p1 in "${DT[@]}"; do
        # Folder name
	name1=$(echo $p1 | bc -l)
        dirname="256_DT_${name1%.*}"
        echo "Creating ${dirname}"
        # Create directory
        mkdir -p "$dirname"

        # Copy files
        cp "$RUN_TEMPLATE" "$dirname/"
        cp "$CODE_EXEC" "$dirname/"

        # Modify parameters inside run.sh
        sed -i "s/^DeltaT=.*/DeltaT=${p1}/" "$dirname/run.sh"
	sleep 2.

	echo "Running for ${dirname}"
        (
            cd "$dirname" || exit
            chmod +x $RUN_TEMPLATE
            nohup ./$RUN_TEMPLATE > output.log 2>&1 &
        )
	sleep 1.
done
