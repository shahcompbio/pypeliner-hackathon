import os

import pypeliner
import pypeliner.managed as mgd
from alignment.config import config
from alignment.utils import helpers
from alignment.workflows import alignment
from alignment.workflows import post_alignment
from alignment.workflows import pre_alignment


def alignment_workflow(args):
    inputs = helpers.load_yaml(args['input_yaml'])
    outdir = args['out_dir']

    outputs = os.path.join(outdir, '{sample_id}', '{sample_id}.bam')
    metrics_output = os.path.join(outdir, '{sample_id}', '{sample_id}_metrics.csv.gz')
    prealignment_tar = os.path.join(outdir, '{sample_id}', '{sample_id}_fastqc.tar.gz')
    postalignment_tar = os.path.join(outdir, '{sample_id}', '{sample_id}_metrics.tar.gz')

    samples = list(inputs.keys())
    fastqs_r1, fastqs_r2 = helpers.get_fastqs(inputs, samples, None)

    sample_info = helpers.get_sample_info(inputs)

    pyp = pypeliner.app.Pypeline(config=args)
    workflow = pypeliner.workflow.Workflow(ctx=helpers.get_default_ctx(docker_image=config.containers('wgs')))

    workflow.setobj(
        obj=mgd.OutputChunks('sample_id', 'lane_id'),
        value=list(fastqs_r1.keys()),
    )

    workflow.subworkflow(
        name="prealign",
        func=pre_alignment.pre_alignment,
        axes=('sample_id', 'lane_id'),
        args=(
            mgd.InputFile('input.r1.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r1),
            mgd.InputFile('input.r2.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r2),
            mgd.Template('prealignment.tar', 'sample_id', template=prealignment_tar),
        )
    )

    workflow.subworkflow(
        name="align",
        func=alignment.alignment,
        args=(
            mgd.InputFile('input.r1.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r1, axes_origin=[]),
            mgd.InputFile('input.r2.fastq.gz', 'sample_id', 'lane_id', fnames=fastqs_r2, axes_origin=[]),
            mgd.OutputFile('output.bam', 'sample_id', template=outputs, axes_origin=[]),
            args['refdir'],
            sample_info,
        ),
    )

    workflow.subworkflow(
        name="postalign",
        func=post_alignment.post_alignment,
        axes=('sample_id',),
        args=(
            mgd.InputFile('output.bam', 'sample_id', template=outputs),
            mgd.OutputFile('metrics.csv.gz', 'sample_id', template=metrics_output, extensions=['.yaml']),
            mgd.OutputFile('metrics.tar.gz', 'sample_id', template=postalignment_tar),
            mgd.InputInstance('sample_id'),
            args['refdir'],
        ),
    )

    pyp.run(workflow)
