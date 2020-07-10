version 1.0

import "prealignment.wdl" as prealignment


struct Fastq {
    String sample_id
    String lane_id
    String fastq1
    String fastq2
}


task MergeOutputs {
    input {
        Array[String] tomerge1
        Array[String] tomerge2
    }

    command {
        echo "${write_lines(tomerge1)} ${write_lines(tomerge2)}"
    }

    output {
        String out = read_string(stdout())
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
        String out = MergeOutputs.out
    }
}


