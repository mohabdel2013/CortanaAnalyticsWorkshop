# Map 1-based optional input ports to variables
dataset <- maml.mapInputPort(1) # class: data.frame

library("tm")

# We assume that the  tweet text is the second columns in the input dataset
text      <- dataset[[1]]

print("Convert to lowercase ....")
preprocessed_text <- sapply(text, tolower)

print("Remove Emails ....")
email_regexp <- "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
preprocessed_text <- gsub(email_regexp, "EmailAddress", preprocessed_text)

print("Remove URLs ....")    
url_regexp <- "(f|ht)(tp)(s?)(://)(.*)[.|/][^ ]+"
preprocessed_text <- gsub(url_regexp, "URL", preprocessed_text)

print("Replace punctuation, special characters and digits with space ....")
preprocessed_text <- gsub("[^a-z]+", " ", preprocessed_text)

print("Remove duplicate characters  ....")
preprocessed_text <- gsub('([[:alpha:]])\\1+', '\\1\\1', preprocessed_text)

print("Create corpus ....")
theCorpus <- Corpus(VectorSource(preprocessed_text))

print("Remove stopword characters  ....")
stopword_list <- setdiff(stopwords("english"), c("no","nor","not" ))
theCorpus <- tm_map(theCorpus, removeWords, stopword_list)

print("Word stemming ....")
theCorpus <- tm_map(theCorpus, stemDocument, language = "english")                                         

data.set <- cbind(dataset, 
                  preprocessed_text = unlist(sapply(theCorpus, "[[", "content")), 
                  stringsAsFactors=F)                                      


# Select data.frame to be sent to the output Dataset port
maml.mapOutputPort("data.set")