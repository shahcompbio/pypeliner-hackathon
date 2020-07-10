version 1.0

import "prealignment.wdl" as prealignment


struct Fastq {
    String sample_id
    String lane_id
    File fastq1
    File fastq2
}


task MergeOutputs {
    input {
        Array[File] tomerge1
        Array[File] tomerge2
    }

    command {
        cat "${sep=' ' tomerge1}" "${sep=' ' tomerge1}" > "result.txt"
    }

    output {
        File out = "result.txt"
    }
}


workflow AlignmentWorkflow {
    input {
        Array[Fastq] fastq_files
    }

    scatter (fastq in fastq_files) {
        call prealignment.PreAlignmentWorkflow {
            input:
                fastq1 = fastq.fastq1,
                fastq2 = fastq.fastq2
        }
    }

    call MergeOutputs {
        input:
            tomerge1=PreAlignmentWorkflow.out1,
            tomerge2=PreAlignmentWorkflow.out2
    }

    output {
        File out = MergeOutputs.out
    }
}


