version 1.0


task RunFastQC {
    input {
        File fastq
    }

    command {
        python -m fire alignment.workflows.pre_alignment.tasks run_fastqc "${fastq}" "fastqc.html" "fastqc.pdf" "./fastqtemp"
    }

    output {
        File html = "fastqc.html"
        File pdf = "fastqc.pdf"
    }
}


task CreateTar {
    input {
        Array[File] files
    }

    command {
        tar -cf compressed.tar ${sep=' ' files}
    }

    output {
        File out = "compressed.tar"
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

    call CreateTar {
        input:
            files=[
                RunFastQC1.html,
                RunFastQC1.pdf,
                RunFastQC2.html,
                RunFastQC2.pdf
            ]
    }

    output {
        File out = CreateTar.out
    }
}


