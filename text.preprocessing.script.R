# Map 1-based optional input ports to variables
dataset <- maml.mapInputPort(1) # class: data.frame

library("tm")

# We assume that the  tweet text is the second columns in the input dataset
tweet_text      <- dataset[[2]]

print("Convert to lowercase ....")
preprocessed_tweet_text <- sapply(tweet_text, tolower)

print("Remove Emails ....")
email_regexp <- "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
preprocessed_tweet_text <- gsub(email_regexp, "EMAIL", preprocessed_tweet_text)

print("Remove URLs ....")    
url_regexp <- "(f|ht)(tp)(s?)(://)(.*)[.|/][^ ]+"
preprocessed_tweet_text <- gsub(url_regexp, "URL", preprocessed_tweet_text)

print("Replace punctuation, special characters and digits with space ....")
preprocessed_tweet_text <- gsub("[^a-z]+", " ", preprocessed_tweet_text)

print("Remove duplicate characters  ....")
preprocessed_tweet_text <- gsub('([[:alpha:]])\\1+', '\\1\\1', preprocessed_tweet_text)

print("Create corpus ....")
theCorpus <- Corpus(VectorSource(preprocessed_tweet_text))

print("Remove stopword characters  ....")
theCorpus <- tm_map(theCorpus, removeWords, stopwords("english"))

print("Word stemming ....")
theCorpus <- tm_map(theCorpus, stemDocument, language = "english")                                         

data.set <- cbind(dataset, 
                  preprocessed_tweet_text = unlist(sapply(theCorpus, "[[", "content")), 
                  stringsAsFactors=F)                                       


# Select data.frame to be sent to the output Dataset port
maml.mapOutputPort("data.set")