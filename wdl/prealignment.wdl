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


task MakeFastQCTar {
    input {
#        File r1_html
        File r1_pdf
#        File r2_html
        File r2_pdf
    }

    command {
        cat "${r1_pdf}" "${r2_pdf}" > "fastqc.tar"
    }

    output {
        File out = "fastqc.tar"
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

    call MakeFastQCTar {
        input: r1_pdf=RunFastQC1.out, r2_pdf=RunFastQC2.out
    }

    output {
        File out = MakeFastQCTar.out
    }
}


