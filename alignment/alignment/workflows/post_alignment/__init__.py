import pypeliner
import pypeliner.managed as mgd
from alignment.config import config
from alignment.utils import helpers
from alignment.workflows.post_alignment.dtypes import dtypes


def post_alignment(
        bam, metrics_csv, metrics_tar, sample_id, refdir,
):
    '''
    calculates bam metrics in bams
    1. picard insert metrics
    2. picard GC metrics
    3. picard wgs metrics
    4. fastqc metrics

    :param config: config containing docker
    images for metrics
    :param bams: sample:bam dictionary
    :param metrics_csv: output csv containing
        metrics
    :param single_node:
    '''

    ref_genome = config.refdir_data(refdir)['paths']['reference']

    picard_wgs_params = config.default_params('alignment')['picard_wgs_params']

    reftype = config.refdir_data(refdir)['params']['reference_type']

    workflow = pypeliner.workflow.Workflow()

    workflow.transform(
        name='markdups',
        ctx=helpers.get_default_ctx(
            memory=20,
            walltime='24:00',
            disk=300
        ),
        func='alignment.workflows.alignment.tasks.markdups',
        args=(
            mgd.InputFile(bam, extensions=['.bai']),
            mgd.TempOutputFile('markdups.bam', extensions=['.bai']),
            mgd.TempOutputFile('markdups_metrics.csv'),
            mgd.TempSpace("temp_markdups"),
        ),
        kwargs={
            'picard_docker': config.containers('picard'),
            'samtools_docker': config.containers('samtools'),
            'mem': '16G'
        }
    )

    workflow.transform(
        name="calc_picard_insert_metrics",
        ctx=helpers.get_default_ctx(
            memory=20,
            walltime='72:00',
            disk=400
        ),
        func='alignment.workflows.post_alignment.tasks.bam_collect_insert_metrics',
        args=(
            mgd.InputFile(bam),
            mgd.TempOutputFile('flagstat_metrics.csv'),
            mgd.TempOutputFile('picard_insert_metrics.csv'),
            mgd.TempOutputFile('picard_insert.pdf'),
            mgd.TempSpace('picard_insert'),
        ),
        kwargs={
            'picard_docker': config.containers('picard'),
            'samtools_docker': config.containers('samtools'),
            'mem': '16G'
        }
    )

    workflow.transform(
        name="calc_picard_gc_metrics",
        func='alignment.workflows.post_alignment.tasks.bam_collect_gc_metrics',
        ctx=helpers.get_default_ctx(
            memory=20,
            walltime='72:00',
            disk=400
        ),
        args=(
            mgd.InputFile(bam),
            ref_genome,
            mgd.TempOutputFile('picard_gc_metrics.csv'),
            mgd.TempOutputFile('picard_gc_summary.csv'),
            mgd.TempOutputFile('picard_gc.pdf'),
            mgd.TempSpace('picard_gc')
        ),
        kwargs={'docker_image': config.containers('picard'), 'mem': '16G'}
    )

    workflow.transform(
        name="calc_picard_wgs_metrics",
        func='alignment.workflows.post_alignment.tasks.bam_collect_wgs_metrics',
        ctx=helpers.get_default_ctx(
            memory=20,
            walltime='72:00',
            disk=400
        ),
        args=(
            mgd.InputFile(bam),
            ref_genome,
            mgd.TempOutputFile('picard_wgs_metrics.csv'),
            picard_wgs_params,
            mgd.TempSpace('picard_wgs')
        ),
        kwargs={'docker_image': config.containers('picard'), 'mem': '16G'}
    )

    workflow.transform(
        name='collect_metrics',
        func='alignment.workflows.post_alignment.tasks.bam_collect_all_metrics',
        ctx=helpers.get_default_ctx(
            memory=10,
            walltime='4:00',
            disk=400
        ),
        args=(
            mgd.TempInputFile('flagstat_metrics.csv'),
            mgd.TempInputFile('picard_insert_metrics.csv'),
            mgd.TempInputFile('picard_wgs_metrics.csv'),
            mgd.TempInputFile('markdups_metrics.csv'),
            mgd.OutputFile(metrics_csv, extensions=['.yaml']),
            sample_id
        ),
        kwargs={
            'main_dtypes': dtypes()['metrics'],
            'insert_dtypes': dtypes()['insert_metrics']
        }
    )

    workflow.transform(
        name='tar',
        func='alignment.utils.helpers.make_tar_from_files',
        axes=('sample_id',),
        args=(
            mgd.OutputFile(metrics_tar),
            [
                mgd.TempInputFile('picard_insert.pdf'),
                mgd.TempInputFile('flagstat_metrics.csv'),
                mgd.TempInputFile('picard_insert_metrics.csv'),
                mgd.TempInputFile('picard_wgs_metrics.csv'),
                mgd.TempInputFile('markdups_metrics.csv'),
                mgd.TempInputFile('picard_gc_metrics.csv'),
                mgd.TempInputFile('picard_gc_summary.csv'),
                mgd.TempInputFile('picard_gc.pdf'),
            ],
            mgd.TempSpace('wgs_metrics')
        )
    )

    return workflow
