import pypeliner
import pypeliner.managed as mgd
from alignment.config import config
from alignment.utils import helpers


def pre_alignment(fastq_r1, fastq_r2, metrics_tar):
    workflow = pypeliner.workflow.Workflow()

    workflow.transform(
        name="fastqc_r1",
        ctx=helpers.get_default_ctx(
            memory=10,
            walltime='48:00',
            disk=400
        ),
        func='alignment.workflows.pre_alignment.tasks.run_fastqc',
        args=(
            mgd.InputFile(fastq_r1),
            mgd.TempOutputFile('R1.html'),
            mgd.TempOutputFile('R1.pdf'),
            mgd.TempSpace('fastqc_R1'),
        ),
        kwargs={
            'docker_image': config.containers("fastqc"),
        }
    )

    workflow.transform(
        name="fastqc_r2",
        func='alignment.workflows.pre_alignment.tasks.run_fastqc',
        ctx=helpers.get_default_ctx(
            memory=10,
            walltime='48:00',
            disk=400
        ),
        args=(
            mgd.InputFile(fastq_r2),
            mgd.TempOutputFile('R2.html'),
            mgd.TempOutputFile('R2.pdf'),
            mgd.TempSpace('fastqc_R2'),
        ),
        kwargs={
            'docker_image': config.containers('fastqc'),
        }
    )

    workflow.transform(
        name='tar',
        func='alignment.utils.helpers.make_tar_from_files',
        axes=('sample_id',),
        args=(
            mgd.OutputFile(metrics_tar),
            [
                mgd.TempInputFile('R2.html'),
                mgd.TempInputFile('R2.pdf'),
                mgd.TempInputFile('R2.html'),
                mgd.TempInputFile('R2.pdf'),
            ],
            mgd.TempSpace('wgs_metrics')
        )
    )

    return workflow
