# Download AgroPortal Snapshot
  
library(jsonlite)

corpusid="agroportal"
outdir="/Volumes/EBI/corpora/"
apikey<-"7429c9a5-5eaf-4f23-8f75-e26113975b83"

ap_ws_ontfull<-"http://data.agroportal.lirmm.fr/ontologies?apikey="
ap_dl_pre<-"http://data.agroportal.lirmm.fr/ontologies/"
ap_dl_post<-paste("/download?apikey=",apikey,sep="")
download_dir<-paste(outdir,corpusid,"/",sep="")
metadata<-paste(outdir,"rosurvey_corpus_",corpusid,".csv",sep="")

ap_ont_rest<-paste(ap_ws_ontfull,apikey,sep="")
ap_raw <- fromJSON(ap_ont_rest, flatten = FALSE, simplifyDataFrame = FALSE, simplifyVector = FALSE, simplifyMatrix = FALSE)

# Make sure a download directory called download exists wherever your working directory is
if (!dir.exists(download_dir)){
  print("Directory does not exist, create and run again: ")
  print(download_dir)
  stop("Directory does not exist, create and run again: ")
}

# Prepare download
t<-unlist(lapply(ap_raw,FUN = function(x) {
  return(x$acronym)
}))
df<-data.frame(o=t)
df$url<-paste(ap_dl_pre,toupper(df$o),ap_dl_post,sep="")
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
