# site_scrapper_public

step 1: input the link into inputsite.txt

step 2: install python packages and requirements: 

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

step 3 run the chain fetcher to fetch content from the site: 

```bash 
python chain_fetcher.py

```

step 4 remove repeatative lines: 

You need know what to remove for each files. Put those lines into remove_lines.txt
then run: 

```bash
python remove_specific_lines.py
```
you might need to do this a few times

step 5 strip all other links and combine all the fetched content into one file

```bash
python strip_links_keep_firstline.py

python format_whitespace.py
```
