version 1.0

struct Fastq {
    String sample_id
    String lane_id
    String fastq1
    String fastq2
}


task MergeOutputs {
    input {
        Array[String] tomerge
    }

    command {
        echo "${write_lines(tomerge)}"
    }

    output {
        String out = read_string(stdout())
    }
}


task RunFastQC {
    input {
        String fastq
    }

    command {
        echo "${fastq}"
    }

    output {
        String out = read_string(stdout())
    }
}


workflow PreAlignmentWorkflow {
    input {
        String fastq1
        String fastq2
    }

    call RunFastQC as RunFastQC1 {
        input: fastq=fastq1
    }

    call RunFastQC as RunFastQC2 {
        input: fastq=fastq2
    }

    output {
        String out1 = RunFastQC1.out
        String out2 = RunFastQC2.out
    }
}


workflow AlignmentWorkflow {
    input {
        Array[Fastq] fastq_files
    }

    scatter (fastq in fastq_files) {
        call PreAlignmentWorkflow {
            input:
                fastq1 = fastq.fastq1,
                fastq2 = fastq.fastq2
        }
    }

    call MergeOutputs {
        input: tomerge=PreAlignmentWorkflow.out
    }

    output {
        String out = MergeOutputs.out
    }
}


