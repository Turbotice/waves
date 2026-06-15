#!/bin/bash
# Values to test
U0=(0.1 0.2 0.3 0.4 0.5)
A0=(0.05 0.1 0.2)
freq=1.2247
# values to be at the resonance of jet oscillation, but not the surface
#freq=(0.825 0.86 0.87 0.88 0.89 0.91 0.92 0.93 0.94 0.96 0.97 0.98 0.99 1.01 1.02 1.03 1.04 1.06 1.08 1.15)
# Original files
RUN_TEMPLATE="run.sh"
CODE_EXEC="./a2.out"
# Loop over all combinations
for p2 in "${U0[@]}"; do
for p1 in "${A0[@]}"; do
        # Folder name
	name1=$(echo $p2*10 | bc -l)
	name2=$(echo $freq*1000 | bc -l)
	name3=$(echo $p1*1000 | bc -l)
        dirname="256_U_0_${name1%.*}_forced_w0_n${name2%.*}_A_${name3%.*}m"
        echo "Creating ${dirname}"
        # Create directory
        mkdir -p "$dirname"

        # Copy files
        cp "$RUN_TEMPLATE" "$dirname/"
        cp "$CODE_EXEC" "$dirname/"

        # Modify parameters inside run.sh
        sed -i "s/^freq=.*/freq=${freq}/" "$dirname/run.sh"
	sed -i "s/^amplitude=.*/amplitude=${p1}/" "$dirname/run.sh"
        sed -i "s/^velocity=.*/velocity=${p2}/" "$dirname/run.sh"
	sleep 2.

	echo "Running for ${dirname}"
        (
            cd "$dirname" || exit
            chmod +x $RUN_TEMPLATE
            nohup ./$RUN_TEMPLATE > output.log 2>&1 &
        )
	sleep 1.
done
done
