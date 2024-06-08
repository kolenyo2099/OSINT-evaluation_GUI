WIP

Make sure the necessary packages are present:
  \[py -m\] pip install -r requirements.txt

In the project directory, create a folder called 'secrets'
In this folder, two files need to be made:
  keys.json
  instructions.txt

The keys.json file should contain the following items:
  {
    "google_cx": "",__
    "google_api_key": "",__
    "open_ai_key": ""__
  }

The instructions.txt file should contain the instructions sent to GPT

Other requirements:
  A [custom Google search engine](https://programmablesearchengine.google.com/controlpanel/all) has to be made__
  First, press the blue button to add a new custom search engine__
  Its name is not important. In the What to search? field, enter the following URLs:__
    www.threadreaderapp.com/*__
    www.threadreaderapp.com/thread/*__
  Next, select your search engine and copy the Search Engine ID__
  This ID should be saved in the keys.json file as the value of google_cx__
  An API key is also required. To create one, first a [Google Cloud project](https://console.cloud.google.com/apis/) must be created__
  Select Credentials in the left column, and create a new API key__
  This API key should be saved in the keys.json file as the value of google_api_key__
  The API must also be enabled. Select Enabled APIs and services on the left and then the blue +Enable APIs and Servces button__
  Search for custom search api and press enable.__

  An OpenAI account (with some balance) is also required__
  An [API key must be created](https://platform.openai.com/settings/profile?tab=api-keys)__
  This API key should be saved as the value of "open_ai_key" in the keys.json file__

Usage:
  py evaluate.py [username or threadreader URL]__

It is also possible to evaluate multiple items at once, seperated by a comma. Usernames and individual threadreader URLs can be mixed.__
For example:__
  py evaluate.py bellingcat,tracelabs,https://threadreaderapp.com/thread/1649032534741663745__
  
