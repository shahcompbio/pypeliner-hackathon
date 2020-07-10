params.ref = "ref/Homo_sapiens.NCBI36.54.dna.chromosome.22.fa"
params.r1 = "data/test.r1.fastq"
params.r2 = "data/test.r2.fastq"

ref_ch = Channel.fromPath(params.ref)
ref_ch_bai = Channel.fromPath(params.ref+'.bai')
ref_ch_amb = Channel.fromPath(params.ref+'.amb')
ref_ch_ann = Channel.fromPath(params.ref+'.ann')
ref_ch_bwt = Channel.fromPath(params.ref+'.bwt')


r1_ch = Channel.fromPath(params.r1)
r2_ch = Channel.fromPath(params.r2)

r1_fq_ch = Channel.fromPath(params.r1)
r2_fq_ch = Channel.fromPath(params.r2)

process fastqc_r1 {
    input:
    file r1 from r1_ch

    output:
    file "r1.html" into fastqc_r1_html

    """
    mkdir -p tempdir/fastqc_r1
    fastqc --outdir=tempdir/fastqc_r1/ $r1
    mv tempdir/fastqc_r1/*.html r1.html
    """
}

process fastqc_r2 {
    input:
    file r2 from r2_ch

    output:
    file "r2.html" into fastqc_r2_html

    """
    mkdir -p tempdir/fastqc_r2
    fastqc --outdir=tempdir/fastqc_r2/ $r2
    mv tempdir/fastqc_r2/*.html r2.html
    """
}


process align_bwa_mem {
    input:
    file r1_fastq from r1_fq_ch
    file r2_fastq from r2_fq_ch
    file ref from ref_ch
    file ref_bai from ref_ch_bai
    file ref_amb from ref_ch_amb
    file ref_ann from ref_ch_ann
    file ref_bwt from ref_ch_bwt

    output:
    file "aligned.bam" into aligned_bam

    """
    bwa mem -M $ref $r1_fastq $r2_fastq | samtools view -bSh - > aligned.bam
    """
}
