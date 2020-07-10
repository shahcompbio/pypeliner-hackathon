
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

|                           | pypeliner | nextflow | toil | cromwell | snakemake | arvados | martian |
|---------------------------|-----------|----------|------|----------|-----------|---------|---------|
| Sub workflows             |y          |e         |      |y         |      y    |         |y        |
| Dynamic splits / merges   |y          |y         |      |y         |      s    |         |y        |
| run python functions      |y          |n         |      |s         |      y    |         |s        |
| run with docker           |y          |y         |      |y         |      s    |         |n        |
| run with singularity      |y          |y         |      |y         |      s    |         |n        |
| launch with docker        |y          |n         |      |n         |      s    |         |n        |
| launch with singularity   |y          |n         |      |n         |      s    |         |n        |
| Azure with low priority   |y          |n         |      |          |      n    |         |n        |
| Azure blob storage        |y          |n         |      |          |      y    |         |n        |
| AWS with spot             |y          |n         |      |          |      n    |         |n        |
| AWS S3                    |y          |n         |      |          |      n    |         |n        |
| WDL support               |n          |n         |      |y         |      n    |         |n        |
| CWL support               |n          |n         |      |y         |      n    |         |n        |
| pass objects between jobs |y          |y         |      |y         |      n    |         |n        |
| Install with?             | pip       |java      |      |java jar  |conda git  |         |exe/go   |
| pros                      |           |          |      |          |           |         |multiplanetary, otherworldly, website is out of this world|
| cons                      |           |          |      |          |           |         |out of this world|


y=yes, n=no, s=sortof, e=experimental

## Strategy

### Preparation

Prior to the hackathon we should:

- [ ] Research available options and complete the above feature matrix (above)
- [x] Assemble a test dataset and pypeliner pipeline to convert to each tool

### Hackathon day

For the hackathon we will work in teams of two.  Each team will choose one or more workflow frameworks to champion
and will work on each gaining as much experience with each framework.

It is suggested that each team divide their responsibilities between:

1. rewriting the pypeliner pipeline
2. deploying the workflow framework locally, on a cluster, and possibly in a cloud environment

In order to allow working in parallel, the individual working on deployment should pick a simple test pipeline
to test deployment.

## Sample Pipeline
Input:
A set of lanes and each lane comes with R1 and R2 fastq files. 


#### Test Data

```
wget  https://wgstestsets.blob.core.windows.net/datasets/alignment_data.tar.gz  
tar -xvf alignment_data.tar.gz  
cd data
```


#### ENVIRONMENT

```
conda install -c bioconda fastqc bwa picard samtools pandas

```

simple alignment pipeline with some pre alignment and post alignment steps:
to test the subworkflow functionality: please try to make 3 sub workflows: pre alignment, alignment and post alignment.

and then build a pipeline that runs these 3 subworkflows.

#### pre alignment

for each lane, run
```
fastqc --outdir=/path/to/an/output/dir /path/to/R1/fastq/file
```

```
fastqc --outdir=/path/to/an/output/dir /path/to/R1/fastq/file
```

this command will generate an html and zip file in the dir. 

*OPTIONAL*
grab these and tarball them
```
mkdir LANE_NAME
cp R1.zip R1.png R2.zip R2.png LANE_NAME
tar -cvf LANE_NAME.tar LANE_NAME
```

#### alignment

*TASK: align*
align each fastq pair to generate on bam per lane

```
bwa mem -M -t 8 /path/to/reference/fasta /path/to/R1/fastq/file /path/to/R2/fastq/file | samtools view -bSh - > /path/to/per/lane/align.bam
```

*TASK: sort*

```
samtools sort -@ 8 -m 5G /path/to/per/lane/align.bam -o /path/to/per/lane/sorted.bam
```

*TASK: merge all per lane bams*
```
picard -Xmx 5G -Xms 5G MergeSamFiles OUTPUT=/path/to/all/lanes/merged.bam SORT_ORDER=coordinate ASSUME_SORTED=true VALIDATION_STRINGENCY=LENIENT MAX_RECORDS_IN_RAM=150000 I=/path/to/per/lane/1/sorted.bam I=/path/to/per/lane/2/sorted.bam
```

*TASK: index*
```
samtools index /path/to/all/lanes/merged.bam /path/to/all/lanes/merged.bam.bai
```

#### post alignment

*TASK: flagstat*

```
samtools flagstat /path/to/all/lanes/merged.bam > /path/to/all/lanes/merged.bam.flagstat
```

*TASK: picard wgs metrics*

```
picard -Xmx5G, -Xms5G CollectWgsMetrics INPUT=/path/to/all/lanes/merged.bam OUTPUT=/path/to/all/lanes/merged.wgsmetrics.txt REFERENCE_SEQUENCE=/path/to/reference.fasta VALIDATION_STRINGENCY=LENIENT TMP_DIR=/path/to/a/throwaway/dir MAX_RECORDS_IN_RAM=150000 
```

*TASK: picard insert metrics*

```
picard -Xmx5G, -Xms5G CollectInsertSizeMetrics INPUT=/path/to/all/lanes/merged.bam OUTPUT=/path/to/all/lanes/merged.insertmetrics.txt HISTOGRAM_FILE=/path/to/all/lanes/merged.inserthistogram.txt VALIDATION_STRINGENCY=LENIENT TMP_DIR=/path/to/a/throwaway/dir MAX_RECORDS_IN_RAM=150000 ASSUME_SORTED=True
```

*TASK: picard gc metrics*

```
picard -Xmx5G, -Xms5G CollectGcBiasMetrics INPUT=/path/to/all/lanes/merged.bam OUTPUT=/path/to/all/lanes/merged.gcmetrics.txt REFERENCE_SEQUENCE=/path/to/reference.fasta S=/path/to/all/lanes/merged.gcmetrics.summary.txt CHART_OUTPUT=/path/to/all/lanes/merged.gcmetrics.chart.txt VALIDATION_STRINGENCY=LENIENT TMP_DIR=/path/to/a/throwaway/dir MAX_RECORDS_IN_RAM=150000 
```

*TASK: picard markdups*

```
picard -Xmx5G, -Xms5G MarkDuplicates INPUT=/path/to/all/lanes/merged.bam OUTPUT=/path/to/all/lanes/merged.markdups.bam METRICS_FILE=/path/to/all/lanes/merged.markdups.txt REMOVE_DUPLICATES=False ASSUME_SORTED=True  VALIDATION_STRINGENCY=LENIENT TMP_DIR=/path/to/a/throwaway/dir MAX_RECORDS_IN_RAM=150000 
```

*OPTIONAL: Merge them*

```
main_dtypes = {  
    'cell_id': 'str',  
  'unpaired_mapped_reads': 'int64',  
  'paired_mapped_reads': 'int64',  
  'unpaired_duplicate_reads': 'int64',  
  'paired_duplicate_reads': 'int64',  
  'unmapped_reads': 'int64',  
  'percent_duplicate_reads': 'float64',  
  'estimated_library_size': 'int64',  
  'total_reads': 'int64',  
  'total_mapped_reads': 'int64',  
  'total_duplicate_reads': 'int64',  
  'total_properly_paired': 'int64',  
  'coverage_breadth': 'float64',  
  'coverage_depth': 'float64',  
  
}

insert_dtypes= {  
    'median_insert_size': 'int64',  
  'mean_insert_size': 'float64',  
  'standard_deviation_insert_size': 'float64'  
}

collect_metrics.CollectMetrics(  
    /path/to/all/lanes/merged.wgsmetrics.txt, /path/to/all/lanes/merged.insertmetrics.txt, /path/to/all/lanes/merged.bam.flagstat, /path/to/all/lanes/merged.markdups.txt, /path/to/all_metrics.txt, 'SA123', main_dtypes, insert_dtypes  
)
collmet.main()
```

the collect metrics code is in alignment/workflows/post_alignment/collect_metrics.py and alignment/utils/csvutils.py
