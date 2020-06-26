# pypeliner-hackathon

## Goals

1. Evaluate workflow systems with the goal of selecting a replacement system for DLP to allow easier distribution to other groups.
2. Gain some experience retooling pypeliner pipelines to understand the amount of effort involved in a complete rewrite.
3. Gain experience with deploying the various competing workflow systems on different clusters / cloud.

## Evaluation Criteria

### General Priorities

1. Wide level of community adoption
2. High quality documentation
3. Compatibility with Dockstore
4. Existing standard workflows (eg. GATK)

### Feature Priorities

1. Composable pipelines / subworkflows
2. Dynamic splits / merges
3. Support for complex objects
4. Docker support
5. Singularity support
6. Cloud support
7. Status monitoring
8. Graph visualization

### Feature Matrix

|                           | pypeliner | nextflow | toil | cromwell | snakemake | arvados |
|---------------------------|-----------|----------|------|----------|-----------|---------|
| Sub workflows             |y          |e         |      |y         |           |         |
| Dynamic splits / merges   |y          |y         |      |y         |           |         |
| run python functions      |y          |n         |      |s         |           |         |
| run with docker           |y          |y         |      |y         |           |         |
| run with singularity      |y          |y         |      |y         |           |         |
| launch with docker        |y          |          |      |n         |           |         |
| launch with singularity   |y          |          |      |n         |           |         |
| Azure with low priority   |y          |          |      |          |           |         |
| Azure blob storage        |y          |          |      |          |           |         |
| AWS with spot             |y          |          |      |          |           |         |
| AWS S3                    |y          |          |      |          |           |         |
| WDL support               |n          |n         |      |y         |           |         |
| CWL support               |n          |n         |      |y         |           |         |
| pass objects between jobs |y          |y         |      |y         |           |         |
| Install with?             | pip       |          |      |java jar  |           |         |

y=yes, n=no, s=sortof, e=experimental

