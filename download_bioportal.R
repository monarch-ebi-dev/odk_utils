# Download BioPortal Snapshot

library(jsonlite)

corpusid="bp"
outdir="/Volumes/EBI/corpora/"
apikey<-"0798b515-1ad4-4585-a9b4-2b4ad0f44f5e"

bp_ws_ontfull<-"http://data.bioontology.org/ontologies_full?apikey="
bp_dl_pre<-"http://data.bioontology.org/ontologies/"
bp_dl_post<-paste("/download?apikey=",apikey,sep="")
download_dir<-paste(outdir,corpusid,"/",sep="")
metadata<-paste(outdir,"rosurvey_corpus_",corpusid,".csv",sep="")

bp_ont_rest<-paste(bp_ws_ontfull,apikey,sep="")
bp_raw <- fromJSON(bp_ont_rest, flatten = FALSE, simplifyDataFrame = FALSE, simplifyVector = FALSE, simplifyMatrix = FALSE)

# Make sure a download directory called download exists wherever your working directory is
if (!dir.exists(download_dir)){
  print("Directory does not exist, create and run again: ")
  print(download_dir)
  quit(9)
}

# Prepare metadata
t<-unlist(lapply(bp_raw,FUN = function(x) {
  return(x$ontology$acronym)
}))
df<-data.frame(o=t)
df$url<-paste(bp_dl_pre,toupper(df$o),bp_dl_post,sep="")
head(df)

# Download
df$filename<-paste(tolower(df$o),".owl",sep = "")
df$filepath<-paste(download_dir,df$filename,sep="")
for(row in 1:nrow(df)) {
  rec = df[row,]
  filename = rec$filepath
  print(paste("Downloading: ",filename))
  if(file.size(filename)<100|!file.exists(filename)) {
    tryCatch({
      print(rec$url)
      download.file(rec$url,filename)
    }, warning = function(war) {
      print(war)
    }, error = function(err) {
      print(paste("MY_ERROR:  ",err))
    }, finally = {
      print("done...")
    })
  } else {
    print("Already downloaded")
  }
}
df$download_success<-file.exists(df$filepath)&file.size(df$filepath)>100
df$corpus<-corpusid
today <- Sys.Date()
df$date<-format(today, format="%B %d %Y")
print(df[!df$download_success,])
write.csv(df,file=metadata)
