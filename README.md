# AI-Translator-Sample

This Repo shows a sample implmentation of a AI Translator web app by using Python and Flask Extending this [sample](https://github.com/) and extening this [sample UI](https://github.com/abhirockzz/azure-cognitive-translateapp) 

# Instruction
- Follow this [tutorial](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-portal%2Cvscode-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli) to deploy the sample app to azure

- The following eniroment varaiables are needed by the app to run 
KEY=<REPLACE-WITH-AI-TRANSLATOR-KEY>
ENDPOINT=<REPLACE-WITH-AI-TRANSLATOR-ENDPOINT>
LOCATION=<REPLACE-WITH-AI-TRANSLATOR-LOCATION>
DOCUMENT_ENDPOINT=<REPLACE-WITH-AI-Document-TRANSLATOR-ENDPOINT>
BLOB_ENDPOINT=<REPLACE-WITH-BLOB-STORAGE-ENDPOINT>
BLOB_KEY=<REPLACE-WITH-BLOB-STORAGE-KEY>
AZURE_SOURCE_BLOB_URL =<REPLACE-WITH-BLOB-STORAGE-CONTAINER-SOURCE>
AZURE_TARGET_BLOB_URL =<REPLACE-WITH-BLOB-STORAGE-CONTAINER-TARGET>
if running it locally create .env file and replace these values and if deploying the cod to azure follow this [tutorial](https://learn.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal) to add application settings 

- This sample has no authentication or authorization implemnted. you can use this [tutorial](https://learn.microsoft.com/en-us/azure/app-service/scenario-secure-app-authentication-app-service) to add app authetication to your deployed app service app 
