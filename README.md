
[![DOI](https://zenodo.org/badge/787321091.svg)](https://zenodo.org/doi/10.5281/zenodo.10978017)

Extracted code for publication. The initial commit of this repository is what has been used in the article. The script `cluster_geneClusters_mash_based.py` should be able to run from here with proper environment setup.

The script has some dependencies and will be maintained as one of the scripts in https://github.com/snail123815/pybioinfo

## Dependencies

1. Working `conda` or `micromamba` program 
2. An environment that have [BiG-SCAPE](https://github.com/medema-group/BiG-SCAPE)
3. An environment that have [mash](https://github.com/marbl/Mash)
4. PFAM database for BiG-SCAPE to use
5. Set all the above parameters in `pyBioinfo_modules/wrappers/_environment_settings.py`

## Running

Help information

```sh
python pyBioinfo/cluster_geneClusters_mash_based.py -h
usage: cluster_geneClusters_mash_based.py [-h] [--cpus CPUS] [--tmp TMP] [--mashClusterRatio MASHCLUSTERRATIO]
                                          [--verboseBigscape VERBOSEBIGSCAPE] --outputPath OUTPUTPATH
                                          p

positional arguments:
  p                     Input dir

options:
  -h, --help            show this help message and exit
  --cpus CPUS           Processes number
  --tmp TMP             temporary files folder
  --mashClusterRatio MASHCLUSTERRATIO
                        Ratio of match/total for two BGC to be clustered
  --verboseBigscape VERBOSEBIGSCAPE
                        add --verbose to bigscape run
  --outputPath OUTPUTPATH
                        Bigscape results
```

SLURM command build:

```sh
#!/bin/bash
#SBATCH   --job-name=mash0.4
#SBATCH --output=mashCluster_BiGMAP_default_0.4cpu_mem.out
#SBATCH  --error=mashCluster_BiGMAP_default_0.4cpu_mem.err
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --mem=900G
#SBATCH --partition=mem
#SBATCH --time=7-00:00:00
#SBATCH --mail-type="END"

TARGET="$PROJ_DIR/antismash_clusters"
CPU=12
MASHCLUSTERRATIO=0.4

TMPCACHE="$PROJ_DIR/temp"$MASHCLUSTERRATIO"cpu"
OUTPUT="$PROJ_DIR/antismash_clusters_res"$MASHCLUSTERRATIO"cpumem"

BASEENV="baseCondaEnv"

SCRATCH=/scratchdata/${SLURM_JOB_USER}/${SLURM_JOB_ID} # fresh for every job
TEMPRES=$SCRATCH/TEMPRES

########################################################
# Command build
CMD="python /home/duc/toolbox-du/pyBioinfo/cluster_geneClusters_mash_based.py"
CMD+=" --cpus $CPU"
CMD+=" --tmp $TMPCACHE"
CMD+=" --outputPath $OUTPUT"
#CMD+=" --outputPath $TEMPRES"
CMD+=" --mashClusterRatio "$MASHCLUSTERRATIO
CMD+=" "$TARGET
########################################################
```

## Acknowledgement

This work was performed using the compute resources from the Academic Leiden Interdisciplinary Cluster Environment (ALICE) provided by Leiden University.

Link: https://pubappslu.atlassian.net/wiki/spaces/HPCWIKI/pages/37519378/About+ALICE
