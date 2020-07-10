import os

from alignment.workflows.post_alignment import collect_metrics
import pypeliner
from alignment.utils import helpers


# taken from single cell
def bam_collect_wgs_metrics(bam_filename, ref_genome, metrics_filename,
                            config, tempdir, mem="2G", docker_image=None):
    helpers.makedirs(tempdir)

    pypeliner.commandline.execute(
        'picard', '-Xmx' + mem, '-Xms' + mem,
        '-XX:ParallelGCThreads=1',
        'CollectWgsMetrics',
                  'INPUT=' + bam_filename,
                  'OUTPUT=' + metrics_filename,
                  'REFERENCE_SEQUENCE=' + ref_genome,
                  'MINIMUM_BASE_QUALITY=' +
                  str(config['min_bqual']),
                  'MINIMUM_MAPPING_QUALITY=' +
                  str(config['min_mqual']),
        'COVERAGE_CAP=500',
        'VALIDATION_STRINGENCY=LENIENT',
                  'COUNT_UNPAIRED=' +
                  ('True' if config['count_unpaired'] else 'False'),
                  'TMP_DIR=' + tempdir,
        'MAX_RECORDS_IN_RAM=150000',
        docker_image=docker_image
    )


def bam_collect_gc_metrics(bam_filename, ref_genome, metrics_filename,
                           summary_filename, chart_filename, tempdir,
                           mem="2G", docker_image=None):
    helpers.makedirs(tempdir)

    pypeliner.commandline.execute(
        'picard', '-Xmx' + mem, '-Xms' + mem,
        '-XX:ParallelGCThreads=1',
        'CollectGcBiasMetrics',
                  'INPUT=' + bam_filename,
                  'OUTPUT=' + metrics_filename,
                  'REFERENCE_SEQUENCE=' + ref_genome,
                  'S=' + summary_filename,
                  'CHART_OUTPUT=' + chart_filename,
        'VALIDATION_STRINGENCY=LENIENT',
                  'TMP_DIR=' + tempdir,
        'MAX_RECORDS_IN_RAM=150000',
        docker_image=docker_image
    )


def bam_flagstat(bam, metrics, **kwargs):
    pypeliner.commandline.execute(
        'samtools', 'flagstat',
        bam,
        '>',
        metrics,
        **kwargs)


def bam_collect_insert_metrics(bam_filename, flagstat_metrics_filename,
                               metrics_filename, histogram_filename, tempdir,
                               mem="2G", picard_docker=None, samtools_docker=None):
    bam_flagstat(
        bam_filename,
        flagstat_metrics_filename,
        docker_image=samtools_docker
    )

    # Check if any paired reads exist
    has_paired = None
    with open(flagstat_metrics_filename) as f:
        for line in f:
            if 'properly paired' in line:
                if line.startswith('0 '):
                    has_paired = False
                else:
                    has_paired = True

    if has_paired is None:
        raise Exception('Unable to determine number of properly paired reads from {}'.format(
            flagstat_metrics_filename))

    if not has_paired:
        with open(metrics_filename, 'w') as f:
            f.write('## FAILED: No properly paired reads\n')
        with open(histogram_filename, 'w'):
            pass
        return

    helpers.makedirs(tempdir)

    pypeliner.commandline.execute(
        'picard', '-Xmx' + mem, '-Xms' + mem,
        '-XX:ParallelGCThreads=1',
        'CollectInsertSizeMetrics',
                  'INPUT=' + bam_filename,
                  'OUTPUT=' + metrics_filename,
                  'HISTOGRAM_FILE=' + histogram_filename,
        'ASSUME_SORTED=True',
        'VALIDATION_STRINGENCY=LENIENT',
                  'TMP_DIR=' + tempdir,
        'MAX_RECORDS_IN_RAM=150000',
        docker_image=picard_docker
    )


def bam_collect_all_metrics(
        flagstat, insert, wgs, markdups_metrics, output, sample_id, main_dtypes=None, insert_dtypes=None
):
    collmet = collect_metrics.CollectMetrics(
        wgs, insert, flagstat, markdups_metrics, output, sample_id, main_dtypes, insert_dtypes
    )
    collmet.main()


def get_igvtools_count(input_bam, counts_file, reference, docker_image=None):
    counts_file_no_tmp = counts_file[:-4]

    cmd = ['igvtools', 'count', input_bam, counts_file_no_tmp, reference]

    pypeliner.commandline.execute(*cmd, docker_image=docker_image)

    os.rename(counts_file_no_tmp, counts_file)
