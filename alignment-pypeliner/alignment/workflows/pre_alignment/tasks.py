import os
import shutil

from alignment.utils import helpers
import pypeliner

import logging


def produce_fastqc_report(fastq_filename, output_html, output_plots, temp_dir,
                          **kwargs):
    helpers.makedirs(temp_dir)

    pypeliner.commandline.execute(
        'fastqc',
        '--outdir=' + temp_dir,
        fastq_filename,
        **kwargs)

    fastq_basename = os.path.basename(fastq_filename)
    if fastq_basename.endswith(".fastq.gz"):
        fastq_basename = fastq_basename[:-len(".fastq.gz")]
    elif fastq_basename.endswith(".fq.gz"):
        fastq_basename = fastq_basename[:-len(".fq.gz")]
    elif fastq_basename.endswith(".fq"):
        fastq_basename = fastq_basename[:-len(".fq")]
    elif fastq_basename.endswith(".fastq"):
        fastq_basename = fastq_basename[:-len(".fastq")]
    else:
        raise Exception("Unknown file type")

    output_basename = os.path.join(temp_dir, fastq_basename)

    shutil.move(output_basename + '_fastqc.zip', output_plots)
    shutil.move(output_basename + '_fastqc.html', output_html)


def run_fastqc(fastq1, html_file, plot_file, tempdir, docker_image=None):
    """
    run fastqc on both fastq files
    run trimgalore if needed, copy if not.
    """
    # empty fastq files
    if os.stat(fastq1).st_size < 100:
        return

    if not os.path.getsize(fastq1) == 0:
        produce_fastqc_report(fastq1, html_file, plot_file, tempdir,
                              docker_image=docker_image)
    else:
        logging.getLogger("single_cell.align.tasks").warn(
            "fastq file %s is empty, skipping fastqc" % fastq1)
