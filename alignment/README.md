1. Download the test data set:
```
wget  https://wgstestsets.blob.core.windows.net/datasets/alignment_data.tar.gz
tar -xvf alignment_data.tar.gz
cd data
```
2. create input.yaml
```
TEST:
  fastqs:
    simulated_lane:
      fastq1: data/test.r1.fastq
      fastq2: data/test.r2.fastq
  bam: bams/TEST.bam
  readgroup_info:
    ID: '{lane_id}'
    PU: '{lane_id}'
    SM: '{sample_id}'
    LB: 'TEST'
    CN: 'BCCAGSC'
    PL: 'ILLUMINA'
```

3. create context.yaml file:
```
docker:
    server: 'docker.io'
    org: pypelinerhackathon
    username: null
    password: null
    mounts:
      local: <your current working dir>
```


4. create pipeline.sh file: 
```
#!/bin/bash

alignment --input_yaml input.yaml \
  --out_dir output --tmpdir temp --pipelinedir pipeline \
  --loglevel DEBUG --submit local \
  --refdir ref --maxjobs 4 \
  --context_config context.yaml
```

5. create launcher.sh
```
#!/bin/bash

docker run --rm -v $PWD:$PWD -w $PWD  -v /var/run/docker.sock:/var/run/docker.sock -v `which docker`:`which docker` pypelinerhackathon/alignment:v0.0.1 sh pipeline.sh
```

4. start the pipeline:
```
sh launcher.sh
``

