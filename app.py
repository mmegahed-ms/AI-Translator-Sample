import time
from flask import Flask, redirect, url_for, request, render_template, session, jsonify, Response
import requests
import os
import uuid
import json
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient
from threading import Thread
load_dotenv()

app = Flask(__name__, static_url_path='/static')



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']

    # Load the values from .env
    key = os.environ['KEY']
    endpoint = os.environ['ENDPOINT']
    location = os.environ['LOCATION']

    # Indicate that we want to translate and the API version (3.0) and the target language
    path = '/translate?api-version=3.0'
    # Add the target language parameter
    target_language_parameter = '&to=' + target_language
    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter

    # Set up the header information, which includes our subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body of the request with the text to be translated
    body = [{'text': original_text}]

    # Make the call using post
    translator_request = requests.post(
        constructed_url, headers=headers, json=body)
    # Retrieve the JSON response
    translator_response = translator_request.json()
    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']

    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )

@app.route('/translate-text', methods=['POST'])
def index_translate_text_post():
    try:
        # Read the JSON data from the request
        request_data = request.get_json()

        # Extract text and target language from the JSON data
        original_text = request_data['text']
        target_language = request_data['to']
        source_language = request_data['from']

        # Load the values from .env
        key = os.environ['KEY']
        endpoint = os.environ['ENDPOINT']
        location = os.environ['LOCATION']

        # Indicate that we want to translate and the API version (3.0) and the target language
        path = '/translate?api-version=3.0'
        # Add the target language parameter
        target_language_parameter = '&to=' + target_language

        # Check if the source language is not empty or null or not equal default value
        if source_language and source_language != 'default':
            # Add the source language parameter
            source_language_parameter = '&from=' + source_language
            # Create the full URL
            constructed_url = endpoint + path + target_language_parameter + source_language_parameter
        # Create the full URL
        constructed_url = endpoint + path + target_language_parameter

        # Set up the header information, which includes our subscription key
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # Create the body of the request with the text to be translated
        body = [{'text': original_text}]

        # Make the call using post
        translator_request = requests.post(
            constructed_url, headers=headers, json=body)
        
        # Retrieve the JSON response
        translator_response = translator_request.json()
        # Retrieve the translation
        translated_text = translator_response[0]['translations'][0]['text']

         # Return the translation as JSON in an array
        return jsonify([{
            'translations': [{'text': translated_text}],
            'detectedLanguage': {
                'language': translator_response[0]['detectedLanguage']['language'],
                'score': translator_response[0]['detectedLanguage']['score']
            }
        }])
    
    

    except Exception as e:
        # Handle exceptions appropriately
        return jsonify({'error': str(e)}), 500


@app.route('/translate-document', methods=['POST'])
def translate_document():
    try:
        # Extract data from the request
        document_target_language = request.form['to']
        document_source_language = request.form['from']
        document_file = request.files['file']
        file_name = document_file.filename

        # Load the values from .env
        key = os.environ['KEY']
        endpoint = os.environ['ENDPOINT']
        location = os.environ['LOCATION']
        blobendpoint = os.environ['BLOB_ENDPOINT']
        blobkey = os.environ['BLOB_KEY']
        
        # Save document to Blob Storage
        blob_service_client = BlobServiceClient(account_url=blobendpoint, credential=blobkey)
        blob_client = blob_service_client.get_blob_client(container="input", blob=str(file_name))

        blob_client.upload_blob(document_file, content_settings=ContentSettings(content_type=document_file.content_type),overwrite=True)
        
        
        # Call the document translation API
        Document_endpoint = os.environ['DOCUMENT_ENDPOINT']
        source_blob_url = os.environ['AZURE_SOURCE_BLOB_URL']
        target_blob_url = os.environ['AZURE_TARGET_BLOB_URL']
        file_name = blob_client.blob_name
        output_file_name = f"{file_name.split('.')[0]}_{document_target_language}.{file_name.split('.')[1]}"

        client = DocumentTranslationClient(Document_endpoint, AzureKeyCredential(key))
        
        # check if source language is not empty or null or not equal default value
        if document_source_language and document_source_language != 'default':   
            poller = client.begin_translation(f"{source_blob_url}/{file_name}", f"{target_blob_url}/{output_file_name}", document_target_language, source_language=document_source_language, storage_type="File")
        else:
            poller = client.begin_translation(f"{source_blob_url}/{file_name}", f"{target_blob_url}/{output_file_name}", document_target_language, storage_type="File")
        result = poller.result()
        

        for document in result:
            print(f"Document ID: {document.id}")
            print(f"Document status: {document.status}")
            if document.status == "Succeeded":
                print(f"Source document location: {document.source_document_url}")
                print(f"Translated document location: {document.translated_document_url}")
                print(f"Translated to language: {document.translated_to}\n")
                # download the translated document using BlobClient
                translated_document_client = blob_client.from_blob_url(document.translated_document_url, credential=blobkey)
                 # download the translated document using BlobClient
                blob_data = translated_document_client.download_blob().readall()

                # create a response with the blob data
                response = Response(blob_data, mimetype='application/octet-stream')
                response.headers.set('Content-Disposition', 'attachment', filename=output_file_name)
                response.headers.set('X-Translation-Status', 'Translation Succeeded')
                response.headers.set('X-Downloaded-File-Name', output_file_name)
                response.headers.set('Content-Type', document_file.content_type) 
                
                # delete the input and output blobs from the storage asynchronously
                #print(f"delete the input and output blobs from the storage asynchronously")
                #Thread(target=delete_blob, args=(blob_client,)).start()
                #Thread(target=delete_blob, args=(translated_document_client,)).start()
                return response
            elif document.error:
                print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")
                return jsonify({'status': "Translation failed"})
            else:
                return jsonify({'status': "Translation in progress"})
    except Exception as e:
            # Handle exceptions
            return jsonify({'error': str(e)}), 500

def delete_blob(blob_client):
    blob_client.delete_blob()
