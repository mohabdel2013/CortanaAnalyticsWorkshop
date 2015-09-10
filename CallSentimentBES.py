
# How this works:
#
# 1. Assume the input is present in a local file (if the web service accepts input)
# 2. Upload the file to an Azure blob - you"d need an Azure storage account
# 3. Call BES to process the data in the blob. 
# 4. The results get written to another Azure blob.

# 5. Download the output blob to a local file
#
# Note: You may need to download/install the Azure SDK for Python.
# See: http://azure.microsoft.com/en-us/documentation/articles/python-how-to-install/

import urllib2
# If you are using Python 3+, import urllib instead of urllib2

import json
import time
from azure.storage import *

def printHttpError(httpError):
 print("The request failed with status code: " + str(httpError.code))

 # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
 print(httpError.info())

 print(json.loads(httpError.read()))
 return


def saveBlobToFile(blobUrl, resultsLabel):
 output_file = "myresults.csv" # Replace this with the location you would like to use for your output file
 print("Reading the result from " + blobUrl)
 try:
     # If you are using Python 3+, replace urllib2 with urllib.request in the following code
     response = urllib2.urlopen(blobUrl)
 except urllib2.HTTPError, error:
    printHttpError(error)
 return

 with open(output_file, "w+") as f:
    f.write(response.read())
 print(resultsLabel + " have been written to the file " + output_file)
 return


def processResults(result):


 first = True
 results = result["Results"]
 for outputName in results:
 result_blob_location = results[outputName]
     sas_token = result_blob_location["SasBlobToken"]
     base_url = result_blob_location["BaseLocation"]
     relative_url = result_blob_location["RelativeLocation"]

     print("The results for " + outputName + " are available at the following Azure Storage location:")
     print("BaseLocation: " + base_url)
     print("RelativeLocation: " + relative_url)
     print("SasBlobToken: " + sas_token)


 #if (first):
 # first = False
 # url3 = base_url + relative_url + sas_token
 # saveBlobToFile(url3, "The results for " + outputName)
 return


import time
def invokeBatchExecutionService():

    storage_account_name = "mohabdel" # Replace this with your Azure Storage Account name
    storage_account_key = "4gcPN4ZMdW6SlrddNr6cngiys6h12rt1grEBpJL4FAvfzsz4XSR1fKMvctfy1h5U6/ktC149WHddi0Kw5epNGg==" # Replace this with your Azure Storage Key
    storage_container_name = "app-reviews" # Replace this with your Azure Storage Container name

 #input_file = "mydata.csv" # Replace this with the location of your input file
    input_blob_name = "Sentiment140.onePercent.sample.tweets.tsv" # Replace this with the name you would like to use for your Azure blob; this needs to have the same extension as the input file 

    api_key = "qplXEpMWX3sJ5A1IN9crWdhtc/YiboUZ+3riX3mlkKErn2BENc1DGkZ4W9cpmcNaXj8lI2NKoKYjWd7iya+D8Q==" # Replace this with the API key for the web service
    url = "https://ussouthcentral.services.azureml.net/workspaces/4ddc51f529344472ba03bccc17adbb05/services/e2f67d2f5cde4a1f91e46789f05c962e/jobs"


    blob_service = BlobService(account_name=storage_account_name, account_key=storage_account_key)

    #print("Uploading the input to blob storage...")
    #data_to_upload = open(input_file, "r").read()
    #blob_service.put_blob(storage_container_name, input_blob_name, data_to_upload, x_ms_blob_type="BlockBlob")
    input_blob_path = "/" + storage_container_name + "/" + input_blob_name
    connection_string = "DefaultEndpointsProtocol=https;AccountName=" + storage_account_name + ";AccountKey=" + storage_account_key

    payload =  {

        "Input": {
            "ConnectionString": connection_string,
            "RelativeLocation": input_blob_path
        },

        "Outputs": {

            "output1": { "ConnectionString": connection_string, "RelativeLocation": "/" + storage_container_name + "/results.tsv" },
        },
        "GlobalParameters": {
}
    }

    body = str.encode(json.dumps(payload))
    headers = { "Content-Type":"application/json", "Authorization":("Bearer " + api_key)}
    print("Submitting the job...")

    # If you are using Python 3+, replace urllib2 with urllib.request in the following code

    # submit the job
    req = urllib2.Request(url + "?api-version=2.0", body, headers)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        printHttpError(error)
        return

    result = response.read()
    job_id = result[1:-1] # remove the enclosing double-quotes
    print("Job ID: " + job_id)


    # If you are using Python 3+, replace urllib2 with urllib.request in the following code
    # start the job
    print("Starting the job...")
    req = urllib2.Request(url + "/" + job_id + "/start?api-version=2.0", "", headers)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        printHttpError(error)
        return

    url2 = url + "/" + job_id + "?api-version=2.0"

    while True:
        print("Checking the job status...")
	    # If you are using Python 3+, replace urllib2 with urllib.request in the follwing code
        req = urllib2.Request(url2, headers = { "Authorization":("Bearer " + api_key) })

        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            printHttpError(error)
            return    

        result = json.loads(response.read())
        status = result["StatusCode"]
        if (status == 0 or status == "NotStarted"):
            print("Job " + job_id + " not yet started...")
        elif (status == 1 or status == "Running"):
            print("Job " + job_id + " running...")
        elif (status == 2 or status == "Failed"):
            print("Job " + job_id + " failed!")
            print("Error details: " + result["Details"])
            break
        elif (status == 3 or status == "Cancelled"):
            print("Job " + job_id + " cancelled!")
            break
        elif (status == 4 or status == "Finished"):
            print("Job " + job_id + " finished!")
        
            processResults(result)
            break
        time.sleep(5) # wait one second
    return

invokeBatchExecutionService()






