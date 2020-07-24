version 1.0


task SplitFastq {
    input {
        File fastq
    }

    command {
        python -m fire biowrappers.components.io.fastq.tasks split_fastq ${fastq} fastq 50
    }

    output {
        Array[File] output_fastqs = glob("fastq*")
    }
}


task BwaAlign {
    input {
        File fastq1
        File fastq2
        Object readgroup_info
        String sample_id
        String lane_id
    }

    command {
        python -m fire alignment.workflows.alignment.tasks align_bwa_mem "${fastq1}" "${fastq2}" \
            /Users/mcphera1/Projects/pypeliner-hackathon/data/ref/Homo_sapiens.NCBI36.54.dna.chromosome.22.fa \
            aligned.bam 8 ${write_json(readgroup_info)} ${sample_id} ${lane_id}
    }

    output {
        File bam = "aligned.bam"
    }
}


task BamSort {
    input {
        File bam
    }

    command {
        python -m fire alignment.workflows.alignment.tasks bam_sort ${bam} sorted.bam
    }

    output {
        File sorted = "sorted.bam"
    }
}


task BamMerge {
    input {
        Array[File] bams
    }

    command {
        python -m fire alignment.workflows.alignment.tasks merge_bams merged.bam ${sep=" " bams}
    }

    runtime {
        continueOnReturnCode: 0
    }

    output {
        File merged = "merged.bam"
    }
}


task BamIndex {
    input {
        File bam
    }

    command {
        samtools index ${bam} ${bam}.bai
    }

    output {
        File bai = "${bam}.bai"
    }
}


workflow BwaAlignmentWorkflow {
    input {
        File fastq1
        File fastq2
        Object readgroup_info
        String sample_id
        String lane_id
    }

    call SplitFastq as SplitFastq1 {
        input: fastq=fastq1
    }

    call SplitFastq as SplitFastq2 {
        input: fastq=fastq2
    }

    scatter(pair in zip(SplitFastq1.output_fastqs, SplitFastq2.output_fastqs)) {
        call BwaAlign {
            input:
                fastq1 = pair.left,
                fastq2 = pair.right,
                readgroup_info = readgroup_info,
                sample_id = sample_id,
                lane_id = lane_id
        }

        call BamSort {
            input: bam = BwaAlign.bam
        }
    }

    call BamMerge {
        input: bams = BamSort.sorted
    }

    call BamIndex {
        input: bam = BamMerge.merged
    }

    output {
        File bam = BamMerge.merged
        File bai = BamIndex.bai
    }
}



