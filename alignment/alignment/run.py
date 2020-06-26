"""
Created on Feb 19, 2018

@author: dgrewal
"""
import argparse
from .alignment import alignment_workflow
import pypeliner

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--input_yaml",
        required=True,
        help='''yaml file with tumour, normal and sampleids'''
    )

    parser.add_argument(
        "--out_dir",
        required=True,
        help='''Path to output directory.'''
    )

    parser.add_argument(
        "--refdir",
        required=True,
        help='''reference data dir'''
    )

    pypeliner.app.add_arguments(parser)

    args = vars(parser.parse_args())

    return args


def main():
    args = parse_args()
    alignment_workflow(args)


if __name__ == "__main__":
    main()
