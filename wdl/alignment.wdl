version 1.0

import "prealignment.wdl" as prealignment
import "bwaalignment.wdl" as bwaalignment


struct Fastq {
    String sample_id
    String lane_id
    File fastq1
    File fastq2
}


task MergeOutputs {
    input {
        Array[File] tomerge
    }

    command {
        cat "${sep=' ' tomerge}" > "result.txt"
    }

    output {
        File out = "result.txt"
    }
}


workflow AlignmentWorkflow {
    input {
        Array[Fastq] fastq_files
        Object readgroup_info
    }

    scatter (fastq in fastq_files) {
        call prealignment.PreAlignmentWorkflow {
            input:
                fastq1 = fastq.fastq1,
                fastq2 = fastq.fastq2
        }
    }

    scatter (fastq in fastq_files) {
        call bwaalignment.BwaAlignmentWorkflow {
            input:
                fastq1 = fastq.fastq1,
                fastq2 = fastq.fastq2,
                readgroup_info = readgroup_info,
                sample_id = fastq.sample_id,
                lane_id = fastq.lane_id
        }
    }

    call MergeOutputs {
        input:
            tomerge=PreAlignmentWorkflow.out
    }

    output {
        File out = MergeOutputs.out
    }
}

