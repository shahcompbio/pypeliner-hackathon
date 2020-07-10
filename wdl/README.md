# WDL

## setup

Download womtool and cromwell from here: https://github.com/broadinstitute/cromwell/releases

## docs

spec: https://github.com/openwdl/wdl/blob/main/versions/1.0/SPEC.md

wdl getting started from terra: https://support.terra.bio/hc/en-us/articles/360037117492-Getting-Started-with-WDL

## running the example

verify: 

```
java -jar womtool-51.jar validate alignment.wdl
```

run:

```
java -jar cromwell-51.jar run test.wdl -i inputs.json
```

