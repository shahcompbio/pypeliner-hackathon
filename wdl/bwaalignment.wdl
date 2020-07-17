version 1.0

task BwaAlignmentWorkflow {
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
        File aligned = "aligned.bam"
    }
}
