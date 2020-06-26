import pypeliner
import pypeliner.managed as mgd
from alignment.config import config
from alignment.utils import helpers


def alignment(
        fastqs_r1,
        fastqs_r2,
        bam_outputs,
        refdir,
        sample_info
):

    workflow = pypeliner.workflow.Workflow()

    workflow.setobj(
        obj=mgd.TempOutputObj('sampleinfo', 'sample_id', axes_origin=[]),
        value=sample_info
    )

    workflow.setobj(
        obj=mgd.OutputChunks('sample_id', 'lane_id'),
        value=list(fastqs_r1.keys()),
    )

    workflow.subworkflow(
        name='align_samples',
        func=align_per_lane,
        axes=('sample_id', 'lane_id'),
        args=(
            mgd.InputFile('input.r1.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r1),
            mgd.InputFile('input.r2.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r2),
            mgd.TempOutputFile('aligned_lanes.bam', 'sample_id', 'lane_id'),
            mgd.InputInstance("sample_id"),
            mgd.InputInstance("lane_id"),
            mgd.TempInputObj('sampleinfo', 'sample_id'),
            refdir
        )
    )

    workflow.transform(
        name='merge_tumour_lanes',
        ctx=helpers.get_default_ctx(
            memory=10,
            walltime='24:00',
            disk=400
        ),
        func="alignment.workflows.alignment.tasks.merge_bams",
        axes=('sample_id',),
        args=(
            mgd.TempInputFile('aligned_lanes.bam', 'sample_id', 'lane_id'),
            mgd.TempOutputFile('merged_lanes.bam', 'sample_id', extensions=['.bai']),
        ),
        kwargs={
            'picard_docker_image': config.containers('picard'),
            'samtools_docker_image': config.containers('samtools')
        }
    )

    samples = sorted(set([v[0] for v in fastqs_r1.keys()]))
    bam_outputs = {sample: bam_outputs[sample] for sample in samples}

    workflow.transform(
        name='markdups',
        ctx=helpers.get_default_ctx(
            memory=20,
            walltime='24:00',
            ncpus=1,
            disk=300
        ),
        func='alignment.workflows.alignment.tasks.markdups',
        axes=('sample_id',),
        args=(
            mgd.TempInputFile('merged_lanes.bam', 'sample_id', extensions=['.bai']),
            mgd.OutputFile('markdups.bam', 'sample_id', fnames=bam_outputs, extensions=['.bai']),
            mgd.TempOutputFile('markdups_metrics', 'sample_id'),
            pypeliner.managed.TempSpace("temp_markdups", "sample_id"),
        ),
        kwargs={
            'picard_docker': config.containers('picard'),
            'samtools_docker': config.containers('samtools'),
            'mem': '16G'
        }
    )


    return workflow


def align_per_lane(fastq_1, fastq_2, out_file, sample_id, lane_id, sample_info, refdir):
    ref_genome = config.refdir_data(refdir)['paths']['reference']

    split_size = config.default_params('alignment')['split_size']

    out_bai = out_file + '.bai'

    workflow = pypeliner.workflow.Workflow()

    workflow.transform(
        name='split_fastq_1',
        ctx=helpers.get_default_ctx(
            memory=4,
            walltime='24:00',
        ),
        func='biowrappers.components.io.fastq.tasks.split_fastq',
        args=(
            pypeliner.managed.InputFile(fastq_1),
            pypeliner.managed.TempOutputFile('read_1', 'split'),
            split_size,
        ),
    )

    workflow.transform(
        name='split_fastq_2',
        ctx=helpers.get_default_ctx(
            memory=4,
            walltime='24:00',
        ),
        func='biowrappers.components.io.fastq.tasks.split_fastq',
        args=(
            pypeliner.managed.InputFile(fastq_2),
            pypeliner.managed.TempOutputFile('read_2', 'split', axes_origin=[]),
            split_size,
        ),
    )

    workflow.transform(
        name='align_bwa_mem',
        axes=('split',),
        ctx=helpers.get_default_ctx(
            memory=8,
            walltime='16:00',
            ncpus=8,
        ),
        func='alignment.workflows.alignment.tasks.align_bwa_mem',
        args=(
            pypeliner.managed.TempInputFile('read_1', 'split'),
            pypeliner.managed.TempInputFile('read_2', 'split'),
            ref_genome,
            pypeliner.managed.TempOutputFile('aligned.bam', 'split'),
            '8',
            sample_info,
        ),
        kwargs={
            'sample_id': sample_id,
            'lane_id': lane_id,
            'docker_image': config.containers('bwa')
        }
    )

    workflow.transform(
        name='sort',
        axes=('split',),
        ctx=helpers.get_default_ctx(
            memory=4,
            walltime='16:00',
        ),
        func='alignment.workflows.alignment.tasks.bam_sort',
        args=(
            pypeliner.managed.TempInputFile('aligned.bam', 'split'),
            pypeliner.managed.TempOutputFile('sorted.bam', 'split'),
        ),
        kwargs={
            'docker_image': config.containers('samtools'),
        }
    )

    workflow.transform(
        name='merge',
        ctx=helpers.get_default_ctx(
            memory=8,
            walltime='72:00',
        ),
        func="alignment.workflows.alignment.tasks.merge_bams",
        args=(
            pypeliner.managed.TempInputFile('sorted.bam', 'split'),
            pypeliner.managed.OutputFile(out_file),
        ),
        kwargs={
            'picard_docker_image': config.containers('picard'),
            'samtools_docker_image': config.containers('samtools')
        }
    )

    workflow.commandline(
        name='index',
        ctx=helpers.get_default_ctx(
            memory=4,
            walltime='16:00',
            docker_image=config.containers('samtools')
        ),
        args=(
            'samtools',
            'index',
            pypeliner.managed.InputFile(out_file),
            pypeliner.managed.OutputFile(out_bai)
        ),
    )

    return workflow
