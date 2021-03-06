import os

import pypeliner
from alignment.utils import helpers
from alignment.utils import vcfutils


def run_museq(
        out, log, reference, interval, museq_params,
        tumour_bam=None, normal_bam=None, return_cmd=False,
        titan_mode=False, docker_image=False
):
    '''
    Run museq script for all chromosomes and merge VCF files

    :param tumour: path to tumour bam
    :param normal: path to normal bam
    :param out: path to the temporary output VCF file for the merged VCF files
    :param log: path to the log file
    :param config: path to the config YAML file
    '''

    if titan_mode:
        cmd = ['museq_het']
    else:
        cmd = ['museq']

    if tumour_bam:
        cmd.append('tumour:' + tumour_bam)
    if normal_bam:
        cmd.append('normal:' + normal_bam)

    interval = interval.split('_')
    if len(interval) == 1:
        interval = interval[0]
    elif len(interval) == 2:
        interval = interval[0] + ':' + interval[1]
    elif len(interval) == 3:
        interval = interval[0] + ':' + interval[1] + '-' + interval[2]
    else:
        raise Exception()

    cmd.extend(['reference:' + reference, '--out', out,
                '--log', log, '--interval', interval, '-v'])

    if not tumour_bam or not normal_bam:
        cmd.extend(['-s'])

    for key, val in museq_params.items():
        if isinstance(val, bool):
            if val:
                cmd.append('--{}'.format(key))
        else:
            cmd.append('--{}'.format(key))
            if isinstance(val, list):
                cmd.extend(val)
            else:
                cmd.append(val)

    if return_cmd:
        return cmd
    else:
        pypeliner.commandline.execute(*cmd, docker_image=docker_image)


def run_museq_one_job(
        tempdir, museq_vcf, reference, intervals, museq_params,
        tumour_bam=None, normal_bam=None, museq_docker_image=None,
        vcftools_docker_image=None, titan_mode=False
):
    '''
    Run museq script for all chromosomes and merge VCF files

    :param tumour: path to tumour bam
    :param normal: path to normal bam
    :param out: path to the temporary output VCF file for the merged VCF files
    :param log: path to the log file
    :param config: path to the config YAML file
    '''

    commands = []
    for i, interval in enumerate(intervals):
        ival_temp_dir = os.path.join(tempdir, str(i))
        helpers.makedirs(ival_temp_dir)
        output = os.path.join(ival_temp_dir, 'museq.vcf')
        log = os.path.join(ival_temp_dir, 'museq.log')

        command = run_museq(
            output, log, reference, interval, museq_params,
            tumour_bam=tumour_bam, normal_bam=normal_bam,
            return_cmd=True, titan_mode=titan_mode
        )

        commands.append(command)

    parallel_temp_dir = os.path.join(tempdir, 'gnu_parallel_temp')
    helpers.run_in_gnu_parallel(commands, parallel_temp_dir, museq_docker_image)

    vcf_files = [os.path.join(tempdir, str(i), 'museq.vcf') for i in range(len(intervals))]
    merge_tempdir = os.path.join(tempdir, 'museq_merge')
    helpers.makedirs(merge_tempdir)
    merge_vcfs(vcf_files, museq_vcf, merge_tempdir, docker_image=vcftools_docker_image)


def merge_vcfs(inputs, outfile, tempdir, docker_image=None):
    helpers.makedirs(tempdir)
    mergedfile = os.path.join(tempdir, 'merged.vcf')
    vcfutils.concatenate_vcf(inputs, mergedfile)
    vcfutils.sort_vcf(mergedfile, outfile, docker_image=docker_image)
