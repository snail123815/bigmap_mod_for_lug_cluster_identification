import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path, PurePath
from typing import Literal

from pyBioinfo_modules.basic.decompress import decompFileIfCompressed
from pyBioinfo_modules.bio_sequences.bio_seq_file_extensions import (
    FNA_EXTENSIONS,
)
from pyBioinfo_modules.wrappers._environment_settings import (
    ANTISMASH_ENV,
    CONDAEXE,
    SHELL,
    withActivateEnvCmd,
)


def findClusterNumberStr(file: Path, numberOnly: bool = False) -> str | None:
    match = clusterNumberPattern.search(file.name)
    if match:
        if not numberOnly:
            return match[0].split(".")[1]
        else:
            return match[0].split(".")[1][-3:]
    else:
        return None


antismashClusterGbkFileNameTest = "NNNNNNNNNNNn.region001.gbk"
clusterGbkGlobTxt = r"*region[0-9][0-9][0-9].gbk"
assert PurePath(antismashClusterGbkFileNameTest).match(clusterGbkGlobTxt)
clusterNumberPattern = re.compile(r"\.region[0-9]{3}\.gbk$")
assert (
    findClusterNumberStr(Path(antismashClusterGbkFileNameTest)) == "region001"
)


def runAntismash(
    inputFilePath: Path,
    title: str | None = None,
    description: str | None = None,
    taxon: Literal["bacteria", "fungi"] = "bacteria",
    completeness: Literal[1, 2, 10] = 2,
    condaExe: Literal["conda", "mamba", "micromamba"] = CONDAEXE,
    condaEnv: Path | None = ANTISMASH_ENV,
    cpu: int = 4,
    output: Path | None = None,
    shell: Literal["bash", "zsh"] = SHELL,
    prefix: str = "antismash",
    addDateTimeToPrefix: bool = False,
    geneFinding: Literal[
        "glimmerhmm", "prodigal", "prodigal-m", "auto", "error"
    ] = "error",
    defaultGeneFinding: str = "prodigal",
    silent: bool = False,
    dry: bool = False,
    overwrite: bool = False,
    existsOk: bool = False,
) -> Path:

    logging.info(f"Running antiSMASH for {inputFilePath}")

    inputFilePath, unzip = decompFileIfCompressed(inputFilePath)

    try:
        if output is None:
            prefix = "_".join(
                item
                for item in [
                    prefix,
                    title,
                    f"level{completeness}",
                ]
                if item is not None
            )
            if addDateTimeToPrefix:
                timeStr = datetime.now().strftime(r"%Y%m%d%H%M")
                prefix += "_" + timeStr
            outdir = inputFilePath.parent / prefix
        else:
            outdir = output
        if (outdir / "index.html").exists():
            if overwrite:
                shutil.rmtree(outdir)
            elif existsOk:
                logging.info(f"Find result file in {outdir}, pass.")
                return outdir.resolve()
            else:
                raise FileExistsError(str(outdir))
        elif outdir.exists():
            shutil.rmtree(outdir)

        cmd = (
            f"antismash --cpus {cpu}"
            + " --minimal"
            + " --skip-zip-file"
            + f" --taxon {taxon}"
            + f" --html-title {prefix}"
            + f" --output-dir {outdir}"
        )
        if inputFilePath.suffix in FNA_EXTENSIONS and geneFinding == "auto":
            cmd += f" --genefinding-tool {defaultGeneFinding}"
        elif geneFinding == "auto":
            cmd += f" --genefinding-tool none"
        else:
            cmd += f" --genefinding-tool {geneFinding}"
        if description is not None:
            cmd += f" --html-description {description}"

        if completeness >= 2:
            cmd = cmd.replace(" --minimal", "")
            cmd += " --cb-knownclusters"
            cmd += " --cb-subclusters"
            cmd += " --asf"
        if completeness >= 3:
            cmd += " --cb-general"
            cmd += " --cc-mibig"
            cmd += " --clusterhmmer"
            cmd += " --pfam2go"
            if taxon == "fungi":
                cmd += " --cassis"
        if completeness >= 4:
            cmd += " --rre"
            cmd += " --fullhmmer"
            cmd += " --tigrfam"
            cmd += " --smcog-trees"

        cmd += f" {inputFilePath}"

        if not silent:
            logging.info(cmd)

        cmd = withActivateEnvCmd(cmd, condaEnv, condaExe, shell)

        if dry:
            logging.info(cmd)
        else:
            commandResult = subprocess.run(
                cmd, capture_output=True, shell=True, executable=shell
            )
            if commandResult.returncode != 0:
                logging.error("Failed antismash:")
                logging.error(cmd)
                logging.error(commandResult.stdout.decode())
                logging.error(commandResult.stderr.decode())
    finally:
        if unzip:
            os.remove(str(inputFilePath))
    logging.info(f"Done antiSMASH for {inputFilePath}")

    return outdir.resolve()
