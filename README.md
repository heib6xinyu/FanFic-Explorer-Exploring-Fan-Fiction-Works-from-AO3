# FanFic Explorer

This Python script allows users to scrape data from the "Archive of Our Own" website, specifically focusing on fanart related to movies and games. It is capable of retrieving detailed information about various articles, including their authors, summaries, tags, and more.

## Features

- Retrieve a list of movies and games.
- Search for specific movies or games through local or online search.
- Obtain detailed information about related articles, including:
  - Article title and URL
  - Author's name and URL
  - Tags associated with the article (genre, warnings, etc.)
  - Summary of the article
  - Detailed metadata and chapter content
- Save the scraped data as JSON files.
- Convert the extracted data into pandas DataFrames for easy manipulation and analysis.

## Requirements

- Python 3.x
- requests
- BeautifulSoup4
- tqdm
- pandas

You can install the required packages using pip:

```bash
pip install requests beautifulsoup4 tqdm pandas
```

## Usage

1. **Clone the repository**

   Start by cloning this repository to your local machine using the following command:

   ```bash
   git clone https://github.com/heib6xinyu/FanFic-Explorer-Exploring-Fan-Fiction-Works-from-AO3.git
   ```

   Navigate to the directory where the repository is cloned.

2. **Running the script**

   To run the script, use the following command in your terminal:

   ```bash
   python main.py
   ```

   Upon execution, the script will initially fetch lists of movies and games. You can perform a search operation by invoking the `local_search` function and providing a search keyword.

   Example:
   ```python
   results = local_search('The Witcher')
   ```

   To scrape data related to a specific movie or game, use the `get_all_info` function with the appropriate parameters.

   Example:
   ```python
   related_articles, related_articles_detail = get_all_info(name, url, num)
   ```

3. **Data storage**

   The script saves the detailed information of the articles in JSON format in the working directory. These files are named `related_articles.json` and `related_articles_detail.json`.

4. **Data analysis**

   You can convert the retrieved data into a pandas DataFrame for further analysis or export it into different formats (like CSV or Excel) using pandas functionalities.

## Caution

This script is for educational purposes only. Please respect Archive of Our Own's [Terms of Service](https://archiveofourown.org/tos). Do not use this script to overload their servers or infringe on the privacy of content creators.

