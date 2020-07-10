import logging
import os
import shutil

import pypeliner
from alignment.utils import helpers


def index(bamfile, indexfile, docker_image=None):
    cmd = ['samtools', 'index', bamfile, indexfile]
    pypeliner.commandline.execute(*cmd, docker_image=docker_image)


def markdups(input, output, metrics, tempdir, mem="2G", picard_docker=None, samtools_docker=None):
    cmd = ['picard', '-Xmx' + mem, '-Xms' + mem,
           '-XX:ParallelGCThreads=1',
           'MarkDuplicates',
           'INPUT=' + input,
           'OUTPUT=' + output,
           'METRICS_FILE=' + metrics,
           'REMOVE_DUPLICATES=False',
           'ASSUME_SORTED=True',
           'VALIDATION_STRINGENCY=LENIENT',
           'TMP_DIR=' + tempdir,
           'MAX_RECORDS_IN_RAM=150000'
           ]

    pypeliner.commandline.execute(*cmd, docker_image=picard_docker)

    index(output, output + '.bai', docker_image=samtools_docker)


def picard_merge_bams(inputs, output, mem="2G", **kwargs):
    if isinstance(inputs, dict):
        inputs = inputs.values()

    cmd = ['picard', '-Xmx' + mem, '-Xms' + mem,
           '-XX:ParallelGCThreads=1',
           'MergeSamFiles',
           'OUTPUT=' + output,
           'SORT_ORDER=coordinate',
           'ASSUME_SORTED=true',
           'VALIDATION_STRINGENCY=LENIENT',
           'MAX_RECORDS_IN_RAM=150000'
           ]

    for bamfile in inputs:
        cmd.append('I=' + os.path.abspath(bamfile))

    pypeliner.commandline.execute(*cmd, **kwargs)


def bam_index(infile, outfile, **kwargs):
    pypeliner.commandline.execute(
        'samtools', 'index',
        infile,
        outfile,
        **kwargs)


def merge_bams(inputs, output, picard_docker_image=None, samtools_docker_image=None):
    output_index = output + '.bai'
    picard_merge_bams(inputs, output, docker_image=picard_docker_image)
    bam_index(output, output_index, docker_image=samtools_docker_image)


def bwa_mem_paired_end(fastq1, fastq2, output,
                       reference, readgroup,
                       numthreads,
                       **kwargs):
    """
    run bwa aln on both fastq files,
    bwa sampe to align, and convert to bam with samtools view
    """

    if not numthreads:
        numthreads = 1

    if not readgroup:
        pypeliner.commandline.execute(
            'bwa', 'mem', '-M',
            '-t', numthreads,
            reference, fastq1, fastq2,
            '|', 'samtools', 'view', '-bSh', '-',
            '>', output,
            **kwargs)
    else:
        try:
            readgroup_literal = '"' + readgroup + '"'
            pypeliner.commandline.execute(
                'bwa', 'mem', '-M', '-R', readgroup_literal,
                '-t', numthreads,
                reference, fastq1, fastq2,
                '|', 'samtools', 'view', '-bSh', '-',
                '>', output,
                **kwargs)
        except pypeliner.commandline.CommandLineException:
            pypeliner.commandline.execute(
                'bwa', 'mem', '-M', '-R', readgroup,
                '-t', numthreads,
                reference, fastq1, fastq2,
                '|', 'samtools', 'view', '-bSh', '-',
                '>', output,
                **kwargs)


def get_readgroup(sample_info, sample_id, lane_id):
    if not sample_id or not lane_id:
        raise Exception('sample and lane ids are required')

    id_str = sample_info.pop('ID') if sample_info else 'ID:{0}_{1}'
    read_group = ['@RG', 'ID:'+id_str.format(sample_id = sample_id, lane_id=lane_id)]

    if sample_info:
        for key, value in sorted(sample_info.items()):
            value = value.format(sample_id=sample_id, lane_id=lane_id)
            read_group.append(':'.join((key, value)))

    read_group = '\\t'.join(read_group)

    return read_group


def samtools_sam_to_bam(samfile, bamfile,
                        **kwargs):
    pypeliner.commandline.execute(
        'samtools', 'view', '-bSh', samfile,
        '>', bamfile,
        **kwargs)


def align_bwa_mem(
        read_1, read_2, ref_genome, aligned_bam, threads, sample_info,
        sample_id=None, lane_id=None, docker_image=None
):

    if lane_id in sample_info:
        sample_info = sample_info[lane_id]

    readgroup = get_readgroup(sample_info, sample_id, lane_id)

    bwa_mem_paired_end(
        read_1, read_2, aligned_bam, ref_genome,
        readgroup, threads, docker_image=docker_image
    )


def bam_sort(bam_filename, sorted_bam_filename, threads=1, mem="2G", docker_image=None):
    pypeliner.commandline.execute(
        'samtools', 'sort', '-@', threads, '-m', mem,
        bam_filename,
        '-o',
        sorted_bam_filename,
        docker_image=docker_image)


