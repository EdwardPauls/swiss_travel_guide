# Swiss Travel Guide


## Run locally:

### Create a virtual environment

```shell
$ python -m venv ~/swiss_travel_guide/
```

### Enter the virtual environment
```shell
$ source ~/swiss_travel_guide/bin/activate
```

### Install deps

```shell
$ pip install -r requirements.txt
```

### Login with gcloud:
```shell
$ gcloud auth login
```

And again for using application default credentials when running locally.

```shell
$  gcloud auth application-default login
```



### Start the server locally

```shell
$ python main.py
```




## Updating translations
Some templates/python files have user facing text that requires translations
into de/fr. These are managed by Flask-Babel
(https://python-babel.github.io/flask-babel/)


Declare any text in a template/python that needs to be translated with the
helper method "_()" from babel.

Example

```
<span class="">{{ _('Start Over') }}</span>
```

To generate/update translations when any string is added or changed

### Extract messages

```shell
$ pybabel extract -F babel.cfg -o messages.pot .
```

### Merge changes

```shell
$ pybabel update -i messages.pot -d translations
```


This will update the files under
/translations/de/LC_MESSAGES/messages.po
/translations/fr/LC_MESSAGES/messages.po

###  Update generated files with the translated strings.

Tip: to get a quick draft going, gemini (chat) is usually pretty good to format
the translations, with a prompt such as:

```
Take the following text and repeated exactly the same, but filling in the "msgstr" field with the text in "msgid" translated into German.If the translated message spans multiple lines, wrap each line in double quotes.

#: templates/index.html:75
msgid ""
"Try something like: 'I'd like to go on a beach holiday with my family in "
"Europe' or 'Show me some popular surf destinations'"
msgstr ""

#: templates/index.html:99
msgid "Find my trip"
msgstr ""
```

###   Compile the translations and submit your CL.

To compile run:

```shell
$ pybabel compile -d translations
```


This will update the files:
```
/translations/de/LC_MESSAGES/messages.mo
/translations/fr/LC_MESSAGES/messages.mo
```


Test the changes locally. What to look for:

*   [ ] Try all functionality in all 3 languages using the top dropdown.
*   [ ] Make sure all styles are correct. Change translations or styles as adequate.
*   [ ] Try the app in Mobile mode in all 3 languages. Check no layouts are broken.

If at looks good submit the changes including the compiled files.


## Deploy

For now the process is quite manual.

*   [ ]  First deploy to a staging instance and ensure it all looks good.

```shell
$  gcloud app deploy --no-promote -v staging
```

Do some tests in the deployed link:

*   [ ] Try suggestion cards, if any.
*   [ ] Write a few queries with region, preferences, months, duration.
*   [ ] Make sure filters can be removed and affect the results.
*   [ ] Click on cities and look at Itineraries, Events and Flights.
*   [ ] Repeat for every language and make sure all looks good.
*   [ ]  Finally update the main instance

```shell
$  gcloud app deploy
```
