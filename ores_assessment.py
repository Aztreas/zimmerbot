import sys
# sys.path.append("..")
import pywikibot
import json, urllib
import datetime

# TLDR: The main function, get_ores_assessment, takes in a list of article names and
# a language (English, Russian, or French). It then prints out each article's name,
# along with an automatically generated (machine learning oooohh) assessment of that
# article (Featured Article, Good Article, A-Class Article, B-Class Article, etc)
# This serves as one possible criterion by which users can sort articles.

# ORES Wiki: https://www.mediawiki.org/wiki/ORES
# ORES Documentation: https://ores.wikimedia.org/v3/

# Base ORES API URL
url = "http://ores.wmflabs.org/v3/scores/"
# url_example = "https://ores.wmflabs.org/v3/scores/enwiki/?models=wp10&revids=34854345"

# Note: We only use wp10 because this is what will give us the current article quality.
# We are not extremely concerned with draftquality

# Unfortunately, only three languages currently support automatic ORES wp10 assessment
# We hope that the impact of this function for sorting by article quality will increase
# as more languages begin to support ORES
ORES_SUPPORTED_WIKIS = {"English": "enwiki",
                    "Russian": "ruwiki",
                    "French": "frwiki"
}

# Create languages dictionary from "list_of_wiki_languages.txt"
def generate_language_dict():
    with open("list_of_wiki_languages.txt", "r") as file:
        lines = file.read().split(",")
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            lines[i] = lines[i].strip("\'")
        dictionary = {lines[i+1]:lines[i] for i in range(0, len(lines), 2)}
    return dictionary

language_dict = generate_language_dict()


###############
#MAIN FUNCTION#
###############

# Returns the ORES automatic article quality assessment for the given article_name and language
def get_ores_assessment(article_names, language):
    if language not in ORES_SUPPORTED_WIKIS:
        print("Sorry, automatic ORES article quality assessment is not available in " + language)
    else:
        with urllib.request.urlopen(build_ores_url(article_names, language)) as url:
            data = json.loads(url.read().decode())
            all_assessments = get_article_assessments(data)
            for i in range(len(article_names)):
                print("Article Name: " + article_names[i])
                print("ORES Assessment: " + all_assessments[i])


##################
#HELPER FUNCTIONS#
##################

# Builds the JSON request URL
def build_ores_url(article_names, language):
    # Get Wikipedia's revision id for the articles' most recent revision (aka the current version)
    language_code = language_dict[language]
    site = pywikibot.getSite(language_code)
    rev_ids = []
    for article_name in article_names:
        page = pywikibot.Page(site, article_name)
        rev_id = page.latest_revision.hist_entry().revid
        rev_ids.append(str(rev_id))
    # The context is essentially the same as the language (only three languages/contexts are supported at this time)
    context = ORES_SUPPORTED_WIKIS[language]

    result = url + context + "/?models=wp10&revids=" + "|".join(rev_ids)

    return result


# Returns the ORES automatic article assessment (see following link for table of assessments:
# https://www.mediawiki.org/wiki/ORES#/media/File:Article_quality_and_importance.wp10bot.enwiki.png)
def get_article_assessments(data):
    print(data)
    scores = []
    # first index 0 is the wiki (enwiki, ruwiki, or frwiki)
    # second index 0 is the rev_id
    scores_json = list(data.values())[0]["scores"]
    for article in scores_json:
        score = scores_json[article]["wp10"]["score"]
        scores.append(score["prediction"])
    return scores


######################
#EXAMPLE / HOW TO USE#
######################

get_ores_assessment(["Pear", "Grape", "Gandhi"], "English")

# Performance notes:
# After an article has been queried, it seems that it is cached automatically, so if it is queried again,
# the process is much faster.


do("2Chains", "English")

site = pywikibot.getSite("en")
page = pywikibot.Page(site, "2Chains")
backlinks = site.pagebacklinks(page, followRedirects=True, filterRedirects=True, namespaces=None, total=num, content=False)
