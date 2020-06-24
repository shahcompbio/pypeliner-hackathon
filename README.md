# pypeliner-hackathon

## Evaluation Criteria

### General Priorities

1. Wide level of community adoption
2. High quality documentation
3. Compatibility with Dockstore
4. Existing standard workflows (eg. GATK)

### Feature Priorities

1. Composable pipelines / subworkflows
2. Dunamic splits / merges
3. Support for complex objects
4. Docker support
5. Singularity support
6. Cloud support
7. Status monitoring
8. Graph visualization


|                           | pypeliner | nextflow | toil | cromwell | snakemake | arvados |
|---------------------------|-----------|----------|------|----------|-----------|---------|
| Sub workflows             |<font color='green'>y</font>|          |      |          |           |         |
| run python functions      |<font color='green'>y</font>|          |      |          |           |         |
| run with docker           |<font color='green'>y</font>|          |      |          |           |         |
| run with singularity      |<font color='green'>y</font>|          |      |          |           |         |
| launch with docker        |<font color='green'>y</font>|          |      |          |           |         |
| launch with singularity   |<font color='green'>y</font>|          |      |          |           |         |
| Azure with low priority   |<font color='green'>y</font>|          |      |          |           |         |
| Azure blob storage        |<font color='green'>y</font>|          |      |          |           |         |
| AWS with spot             |<font color='green'>y</font>|          |      |          |           |         |
| AWS S3                    |<font color='green'>y</font>|          |      |          |           |         |
| WDL support               |<font color='red'>n</font>|          |      |          |           |         |
| CWL support               |<font color='red'>n</font>|          |      |          |           |         |
| pass objects between jobs |<font color='green'>y</font>|          |      |          |           |         |
| Install with?             | pip       |          |      |          |           |         |
