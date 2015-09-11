# Cortana Analytics Workshop: Natural Language Understanding
In this tutorial, we'll explain how to to build an experiment for sentiment analysis using *Microsoft Azure Machine Learning Studio*. Sentiment analysis is a special case of text mining that is increasingly important in business intelligence and and social media analysis. For example, sentiment analysis of user reviews and tweets can help companies monitor public sentiment about their brands, or help consumers who want to identify opinion polarity before purchasing a product. 
This tutorial demonstrates the use of the **Feature Hashing**, **Execute R Script** and **Filter-Based Feature Selection** modules to train a sentiment analysis engine. We use a data-driven machine learning approach instead of a lexicon-based approach, as the latter is known to have high precision but low coverage compared to an approach that learns from a corpus of annotated tweets. 
The hashing features are used to train a model using the **Two-Class Support Vector Machine** (SVM), and the trained model is used to predict the public opinion on movies given Amazon free-text reviews. In general, the output predictions can be aggregated over all the reviews/tweets containing a certain keyword, such as brand, celebrity, product, book names, etc in order to find out the overall sentiment around that keyword. The tutorial is generic enough that you could use this framework to solve any text classification task given a reasonable amount of labeled training data.

##Experiment Creation

The main steps of the experiment are:

- [Step 1: Get data]
- [Step 2: Text preprocessing using R]
- [Step 3: Feature engineering]
- [Step 4: Split the data into train and test]
- [Step 5: Train prediction model]
- [Step 6: Evaluate model performance]
- [Step 7: Publish prediction web service]
- [Step 8: Consume the prediction web service]
- [Step 9: Visualize-the-output]

[Step 1: Get data]:#step-1-get-data
[Step 2: Text preprocessing using R]:#step-2-pre-process-text
[Step 3: Feature engineering]:#step-3-feature-engineering
[Step 4: Split the data into train and test]:#step-4-split-data
[Step 5: Train prediction model]:#step-5-train-model
[Step 6: Evaluate model performance]:#step-6-evaluate-model
[Step 7: Publish prediction web service]:#step-7-publish-web-service
[Step 8: Consume the prediction web service]:#step-8-consume-web-service
[Step 9: Visualize-the-output]:#step-9-visualize-the-output

 ![][image-overall]

### <a name="step-1-get-data"></a>Step 1: Get data

The data used in this experiment is [Sentiment140 dataset](http://help.sentiment140.com/) (http://help.sentiment140.com), a publicly available data set created by three graduate students at Stanford University: Alec Go, Richa Bhayani, and Lei Huang. The data comprises approximately 1,600,000  automatically annotated tweets. 

The tweets were collected by using the Twitter Search API and keyword search. During automatic annotation, any tweet with positive emoticons, like :), were assumed to bear positive sentiment, and tweets with negative emoticons, like :(, were supposed to bear negative polarity. Tweets containing both positive and negative emoticons were removed. Additional information about this data and the automatic annotation process can be found in the technical report written by Alec Go, Richa Bhayani and Lei Huang, *Twitter Sentiment Classification using Distant Supervision*, in 2009. 

For this experiment, we extracted a 10% sample of the data. The sample is shared as a Blob in a Windows Azure Storage public account and in GitHub (https://github.com/mohabdel2013/CortanaAnalyticsWorkshop). You can get the full data set from the Sentiment140 dataset home page.  

Load the dataset that contains the text column into the experiment, using one of the following methods:

- **Option 1:**	Click **New**, and select **DATASET**, and then select **FROM LOCAL FILE**.
- **Option 2:** Add a **Reader** module to the experiment if you need to load  the data from Azure Storage.

 ![][image-data-reader]

 

Each instance in the data set has 6 fields:

* sentiment_label - the polarity of the tweet (0 = negative, 2 = neutral, 4 = positive)
* tweet_id - the id of the tweet 
* time_stamp - the date of the tweet (Sat May 16 23:58:44 UTC 2009)
* target - the query (lyx). If there is no query, then this value is NO_QUERY.
* user_id - the user who posted the tweet 
* tweet_text - the text of the tweet 

We have uploaded only the two fields that are required for training as shown below:

![][image-data-view]

### <a name="step-2-pre-process-text"></a>Step 2: Text preprocessing using R

Unstructured text such as a tweet usually requires some preprocessing before it can be analyzed. The **Execute R Script** is used to do any of the following preprocessing steps: remove punctuation marks, remove special character and digits, remove URLs, remove E-mail addresses, Porter's word stemming  or case normalization. You can download the R script (text.preprocessing.script.R) from GitHub (https://github.com/mohabdel2013/CortanaAnalyticsWorkshop).
 
![][image-text-preprocess]

After the text was cleaned, use the **Metadata Editor** module to mark all the input columns as non-features. The reason is that we want the learner to ignore the input columns including the source text and not use it as features when training the model, but rather to use the hashing features that we extract in the next step.   

![][image-metadata-editor]

### <a name="step-3-feature-engineering"></a> Step 3: Feature engineering
#### Feature hashing
The **Feature Hashing** module can be used to represent variable-length text documents as equal-length numeric feature vectors. An added benefit of using feature hashing is that it reduces the dimensionality of the data, and makes lookup of feature weights faster by replacing string comparison with hash value comparison.

If we set the number of hashing bits to 17 and the number of N-grams to 2. With these settings, the hash table can hold 2^17 or 131,072 entries in which each hashing feature will represent one or more unigram or bigram features. For many problems, this is plenty, but in some cases, more space is needed to avoid collisions. You should experiment with a different number of bits and evaluate the performance of your machine learning solution. 

![][image-feat-hash]

#### Feature selection
The classification complexity of a linear model is linear with respect to the number of features. However, even with feature hashing, a text classification model may have some irrelevant/non-discriminating features for a good solution. Therefore, we can use the **Filter Based Feature Selection** module to select a compact feature subset from the exhaustive list of extracted hashing features. The aim is to reduce the computational complexity without affecting classification accuracy. 

Select the Chi-squared score function to rank the hashing features in descending order, then return the top 20,000 most relevant features with respect to the sentiment label, out of the 2^17 extracted features. 

![][image-feature-selection]

### <a name="step-4-split-data"></a>Step 4: Split the data into train and test

The *Split* module in Azure ML is used to split the data into train and test sets where the split is stratified. The stratification will maintain the class ratios into the two output groups. We use the first 80% of the Sentiment140 sample tweets for training and the remaining 20% for testing the performance of the trained model.

![][image-data-split]

### <a name="step-5-train-model"></a>Step 5: Train prediction model

To train the model, we connected the text features created in the previous steps (the training data) to the ***Train Model** module. Microsoft Azure Machine Learning Studio supports a number of learning algorithms but we select SVM for illustration. 

![][image-train-model]

The parameters used in the **Two-Class Support Vector Machine** module are shown in the following graphic:

![][image-svm-parameters]

### <a name="step-6-evaluate-model"></a>Step 6: Evaluate trained model performance

In order to evaluate the generalization ability of the trained Support Vector Machine model on unseen data,  the output model and the test data set are connected to the *Score Model* module in order to score the tweets of the test set. Then connect the out predictions to the *Evaluate Model* module in order to get a number of performance evaluation metrics as shown below. Note that the performance mentioned below is resulting from training the model on the full Sentiment140 dataset. In order to reproduce the same performance, please replace the 10% sample data attached to the experiment with the full data set.  

Finally, add the **Evaluate  Model** module, to get the evaluation metrics (ROC, precision/recall, and lift) as shown in the following charts. 

Note that the metrics shown here resulted from training the model on the full Sentiment140 dataset. Therefore, to reproduce these results, you should replace the 10% sample dataset with the full data set.  
   
![][image-evaluate-model]

#### ROC curve
 
![][image-ROC]

#### Precision/Recall curve
![][image-PR-Curve]

#### Lift curve

![][image-Lift]

### <a name="step-7-publish-web-service"></a>Step 7: Publish prediction web service

A key feature of Azure Machine Learning is the ability to easily publish models as web services on Windows Azure. In order to publish the trained sentiment prediction model, first we must save the trained model. To do this, just click the output port of the **Train Model** module and select **Save as Trained Model**.

The output of this step is two endpoints: RRS (Request Response Service) or BES (Batch Execution Service). When using RRS, only one text instance is classified at a time. When using BES, a batch of text instances can be sent for classification at the same time.  

![][image-save-trained-model]

Next, we created a new experiment that has only the scoring module, with the saved model attached. We also provided a sample schema for the input data, which we created by sampling one of the tweets in the **`Sentiment140`** dataset. 

Web service entry and exit points are defined using the special Web Service modules. Note that the **Web service input** module is attached to the node in the experiment where input data would enter.

![][image-scoring-exp]

Add the following **Project Column** module to discard hashing features from  the dataset and to keep only the input columns in addition to **Scored Labels** and  **Scored Probabilities**.    

![][image-output-preparation]

After successfully running the experiment, it can be published by clicking **Publish Web Service** at the bottom of the experiment canvas.

Go to the web service web page,
**1.**	Copy the **API key** for your published web service.
**2.**  Select **BATCH EXECUTION**, Copy the **POST Request URI**.


![][image-publish-web-service]

For more information about how to publish a web service, see [this tutorial](http://azure.microsoft.com/en-us/documentation/articles/machine-learning-walkthrough-5-publish-web-service/).

### <a name="step-8-consume-web-service"></a>Step 8: Consume the prediction web service

**8.1.** Download the Amazon movie DVDs reviews TSV file (reviews_the hunger games_and_Frozen.tsv) from GitHub (https://github.com/mohabdel2013/CortanaAnalyticsWorkshop).

**8.2.** Upload the reviews TSV file to your Azure Storage container.

**8.3.** You have two options to run your sentiment analysis model. The RRS or BES web service endpoints.

**1.**	Based your language preference, copy the R/Python/C# sample code from the web service page into your IDE. Do not forget to update the sample code with **API key** and **POST Request URI**.

**2.**	Click **New**, and select **NOTEBOOK**, and then select **Python 2 Blank Notebook**. Download the Python script (CallSentimentBES.py) from GitHub (https://github.com/mohabdel2013/CortanaAnalyticsWorkshop) then copy and paste its contents into the new notebook. Do not forget to update the sample code with **API key** and **POST Request URI**. Run the notebook on the reviews TSV file stored in your Azure Storage.

![][ipython-notebook]

**8.4.** Download the prediction results from your Azure Storage.

### <a name="step-9-visualize-the-output"></a>Step 9: Visualize the prediction output

**9.1.** Open Power BI Desktop 

**9.2.** Download the Python script (Demo.pbix) from GitHub (https://github.com/mohabdel2013/CortanaAnalyticsWorkshop).

**9.3.** Connect to your local copy of the results file or the Blob in your Azure Storage account. 

![][powerbi-desktop]

### References

**1.** Azure Marketplace Text Analytics API (https://datamarket.azure.com/dataset/amla/text-analytics)
**2.** Azure Machine learning text classification template (http://gallery.azureml.net/browse?s=text)

<!-- Images -->
[image-data-reader]:./media/data-reader.PNG
[image-data-view]:./media/data-view.PNG
[image-overall]:./media/training-exp.PNG
[image-text-preprocess]:./media/text-preprocessing-R.PNG
[image-metadata-editor]:./media/metadata-editor.PNG
[image-feat-hash]:./media/feature-hashing.PNG
[image-data-split]:./media/data-split.PNG
[image-feature-selection]:./media/feature-selection.PNG
[image-train-model]:./media/train-model.PNG
[image-svm-parameters]:./media/svm-parameters.PNG
[image-save-trained-model]:./media/save-trained-model.PNG
[image-scoring-exp]:./media/scoring-exp.PNG
[image-evaluate-model]:./media/evaluate-model.PNG
[image-ROC]:./media/ROC.PNG
[image-PR-Curve]:./media/PR-Curve.PNG
[image-Lift]:./media/Lift.PNG
[image-publish-web-service]:./media/publish-web-service.PNG
[image-output-preparation]:./media/output-preparation.PNG
[ipython-notebook]:./media/ipython-notebook.PNG
[powerbi-desktop]:./media/powerbi-desktop.PNG