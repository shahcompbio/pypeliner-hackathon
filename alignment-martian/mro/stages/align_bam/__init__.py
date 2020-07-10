import os
import yaml
import subprocess

__MRO__ = """
stage SAMPLE_SETUP(
    in  path inventory,
    out map samples,
    out map batch,
    src py "stages/sample_setup",
)
"""

def main(args, outs):

    r1 = getattr(args,'r1')['sample1']
    r2 = getattr(args,'r1')['sample1']
    ref = getattr(args,'ref')['sample1']

    outbam = getattr(outs,'bamfile')

    cmd = ['bwa', 'mem', '-M', ref, r1, r2, '|', 'samtools', 'view', '-bSh', '-', '>', outbam]

    cmd = ' '.join(cmd)
 
    subprocess.check_call(cmd, shell=True)


