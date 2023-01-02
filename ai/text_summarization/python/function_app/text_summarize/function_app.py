import azure.functions as func
import logging
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

app = func.FunctionApp()

# Load AI url and secrets from Env Variables in Terminal before running, 
# e.g. `export AI_URL=https://***.cognitiveservices.azure.com/`
key = os.getenv('AI_SECRET', 'SETENVVAR!') 
endpoint = os.getenv('AI_URL', 'SETENVVAR!') 

# Authenticate the client using your key and endpoint 
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client

client = authenticate_client()

# Example method for summarizing text
def ai_summarize_txt(client, document):
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        ExtractSummaryAction
    ) 

    poller = client.begin_analyze_actions(
        document,
        actions=[
            ExtractSummaryAction(max_sentence_count=4)
        ],
    )

    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            logging.info("...Is an error with code '{}' and message '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            logging.info("Returning summarized text:  \n{}".format(
                " ".join([sentence.text for sentence in extract_summary_result.sentences]))
            )

@app.function_name(name="summarize_function")
@app.blob_trigger(arg_name="myblob", path="test-samples-trigger/{name}",
                  connection="")
@app.blob_output("test-samples-output/{name}-output.txt")
def test_function(myblob: func.InputStream):
   logging.info(f"Triggered item: {myblob.name}\n")

   summarizedText = ai_summarize_txt(client, myblob)
   logging.info(f"\n *****Summary***** \n{summarizedText}");

   return summarizedText
