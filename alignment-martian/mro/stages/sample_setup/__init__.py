import os
import yaml


__MRO__ = """
stage SAMPLE_SETUP(
    in  path inventory,
    out map samples,
    out map batch,
    src py "stages/sample_setup",
)
"""

def main(args, outs):
    outs.r1 = dict()
    outs.r2 = dict()
    outs.ref = dict()


    samples = yaml.load(open(args.inventory))

    ref = samples['ref']

    for sample in samples['fastqs']:
        outs.r1[sample] = samples['fastqs'][sample]['r1']
        outs.r2[sample] = samples['fastqs'][sample]['r2']
        outs.ref[sample] = ref


