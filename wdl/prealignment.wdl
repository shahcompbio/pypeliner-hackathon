version 1.0


task RunFastQC {
    input {
        File fastq
    }

    command {
        head "${fastq}" > "fastqc.out"
    }

    runtime {
        continueOnReturnCode: 0
    }

    output {
        File out = "fastqc.out"
    }
}


workflow PreAlignmentWorkflow {
    input {
        File fastq1
        File fastq2
    }

    call RunFastQC as RunFastQC1 {
        input: fastq=fastq1
    }

    call RunFastQC as RunFastQC2 {
        input: fastq=fastq2
    }

    output {
        File out1 = RunFastQC1.out
        File out2 = RunFastQC2.out
    }
}


