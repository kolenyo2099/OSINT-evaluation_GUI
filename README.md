# OSINT-evaluation
Trust in OSINT
MA Thesis
New Media and Digital Culture
University of Amsterdam
Cees van Spaendonck
12425001

This tool ...

## Prerequisite
### Requirements
Make sure the necessary packages are present:
  \[py -m\] pip install -r requirements.txt

In the project directory, create a folder called 'secrets'
In this folder, two files need to be made:
  keys.json
  instructions.txt

The keys.json file should contain the following items:
  {
    "google_cx": "",
    "google_api_key": "",
    "open_ai_key": ""
  }

The instructions.txt file should contain the instructions sent to GPT

### Custom Google search engine
  - A [custom Google search engine](https://programmablesearchengine.google.com/controlpanel/all) has to be made
  - First, press the blue button to add a new custom search engine
  - Its name is not important. In the What to search? field, enter the following URLs:
    www.threadreaderapp.com/*
    www.threadreaderapp.com/thread/*
  - Next, select your search engine and copy the Search Engine ID
  - This ID should be saved in the keys.json file as the value of google_cx
  - An API key is also required. To create one, first a [Google Cloud project](https://console.cloud.google.com/apis/) must be created
  - Select Credentials in the left column, and create a new API key
  - This API key should be saved in the keys.json file as the value of google_api_key
  - The API must also be enabled. Select Enabled APIs and services on the left and then the blue +Enable APIs and Servces button
  - Search for custom search api and press enable.
### Open AI Key
  - An OpenAI account (with some balance) is also required
  - An [API key must be created](https://platform.openai.com/settings/profile?tab=api-keys)
  - This API key should be saved as the value of "open_ai_key" in the keys.json file

## Usage:
```
  py evaluate.py [username or threadreader URL] [--force_scrape=] [--skip_scrape=] [--skip_evaluation=]
```
It is possible to evaluate multiple items at once, seperated by a comma. Usernames and individual threadreader URLs can be mixed.
For example:
```
  py evaluate.py bellingcat,tracelabs,https://threadreaderapp.com/thread/1649032534741663745
```

Optionally, some parts of the process in the tool can be forced or skipped based on the above mentioned optional flags. These include
Scraping can be forced to try and add results previously not found, even if list of threads/tweets is already present. This can be done with the --force_scrape flag:
```
  py evaluate.py [bellingcat] --force_scrape=True
```
Scraping can also be skipped, which causes the tool to directly evaluate threads/tweets in the local_data folder, if for example only the evaluation instructions have to be tested. This can be done with the --skip_scrape flag:
```
  py evaluate.py [bellingcat] --skip_scrape=True
```
Evaluation can also be skipped, which causes the tool to only search for new threads/tweets, in order to reduce the runtime by not evaluating threads. This can be done with the --skip_evaluation flag:
```
  py evaluate.py [bellingcat] --skip_evaluation=True
```

