#WIP

###Requirements
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

###Custom Google search engine
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
###Open AI Key
  - An OpenAI account (with some balance) is also required
  - An [API key must be created](https://platform.openai.com/settings/profile?tab=api-keys)
  - This API key should be saved as the value of "open_ai_key" in the keys.json file

##Usage:
```
  py evaluate.py [username or threadreader URL]
```

It is also possible to evaluate multiple items at once, seperated by a comma. Usernames and individual threadreader URLs can be mixed.
For example:
```
  py evaluate.py bellingcat,tracelabs,https://threadreaderapp.com/thread/1649032534741663745
```
  
