version 1.0


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


