# Download OBO Snapshot
  
library(yaml)

corpusid="obo20190313"
outdir="/data/corpora/"
obo="http://obofoundry.org/registry/ontologies.yml"

download_dir<-paste(outdir,corpusid,"/",sep="")
metadata<-paste(outdir,"patosurvey_corpus_",corpusid,".csv",sep="")
obo_raw <- yaml.load_file(obo)
head(obo_raw)

# Make sure a download directory called download exists wherever your working directory is
if (!dir.exists(download_dir)){
  print("Directory does not exist, create and run again: ")
  print(download_dir)
  stop("Directory does not exist, create and run again: ")
}

processOBO <-function(x) {
  id=x$id
  obsolete="FALSE"
  purl="unknown"
  email="unknown"
  if(!is.null(x[["ontology_purl"]])){
    purl = x[["ontology_purl"]]
  }
  if(!is.null(x[["is_obsolete"]])){
    obsolete = x[["is_obsolete"]]
  }
  if(!is.null(x[["contact"]])){
    email = x[["contact"]][["email"]]
  }
  return(c(obsolete,id,purl,email))
}

# Prepare OBO Metadata
t<-unlist(lapply(obo_raw$ontologies,processOBO))
df<-data.frame(email=t[seq(4, length(t), 4)],url=t[seq(3, length(t), 4)],o=t[seq(2, length(t), 4)],obsolete=t[seq(1, length(t), 4)])
df$url<-as.character(df$url)
df$o<-gsub("-","",as.character(df$o))
df$obsolete<-as.character(df$obsolete)
df$tdl<-gsub(".*@","",df$email)
print("first records obo")
tail(df)
df<-df[df$obsolete!="TRUE"&df$url!="unknown",]
tail(df)

# Download (all downloader should have identical)
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

for(f in df$filepath) {
  if(file.exists(f)&file.size(f)<100)
    file.remove(f)
}

print("Not successfully downloaded: ")
for(f in df$filepath) {
  if(!file.exists(f))
    print(f)
}

df$download_success<-file.exists(df$filepath)
df$obsolete<-NULL
df$corpus<-corpusid
today <- Sys.Date()
df$date<-format(today, format="%B %d %Y")
print(df[!df$download_success,])
write.csv(df,file=metadata)

