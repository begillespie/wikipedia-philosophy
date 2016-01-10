'''
Based on the title text of the famous XKCD comic, 'Extended Mind'
xkcd.com/903:
Wikipedia trivia: if you take any article, click on the first link in the
article text not in parentheses or italics, and then repeat, you will eventually
end up at 'Philosophy'

To use, run the script in one of 3 ways:
1. With an article title to start from that article.
2. With the word 'random' to start from a random article.
3. With no arguments to start from the article of the day.
'''

import requests, re, sys
from bs4 import BeautifulSoup

chain = []
# A list of mediawiki namespaces that we do not want to follow.
# The urls show up in the form of '/wiki/Namespace:Page'
sys_pages = ['Help', 'Special', 'Wikipedia', 'Portal']

def get_page(article):
    url = 'https://en.wikipedia.org' + article
    print(url)

    # Check for a loop of articles
    if url in chain:
        print("Article loop found")
        chain.append(url)
        close()
    chain.append(url)

    if len(chain) == 100:
        print('This one seems to diverge.')
        close()

    if article == '/wiki/Philosophy':
        print('PHILOSOPHY')
        close()

    r = requests.get(url)
    print(r.status_code)
    if r.status_code != 200:
        print('Link not found')
        close()

    page = BeautifulSoup(r.text, 'html.parser')
    # Find <p> tags that are direct descendants of the content element
    body = page.find(id = 'mw-content-text').find_all('p', recursive=False)

    for para in body:
        # Get rid of some tags that won't hold what we're looking for:
        [t.decompose() for t in para(['table', 'i', 'sup'])]
        para = BeautifulSoup(remove_parentheses(str(para)), 'html.parser')
        if 'href' in str(para):
            links = para.find_all('a')
            if links:
                for l in links:
                    next_link = l.get('href')
                    # Check that this is an internal link. Also, I chose to not
                    # follow links to id tags
                    if next_link[0:6] == '/wiki/' and '#' not in next_link:
                        if not any(next_link.startswith('/wiki/' + t + ':') for \
                        t in sys_pages):
                            get_page(next_link)

def get_featured_article():
    mainpage = requests.get('https://en.wikipedia.org/wiki/Main_Page')
    mp = BeautifulSoup(mainpage.text, 'html.parser')
    # According to the rules, only the link to Today's Featured Article is in
    # bold and it must be the first link in the blurb.
    get_page(mp.find(id = 'mp-tfa').b.a.get('href'))

def remove_parentheses(string):
    p = 0 #Track parentheses
    b = 0 #Track angular brackets
    string_out = ''
    for c in string:
        if c == '(':
            p += 1
            if b == 0: #Not inside a tag
                c = ''
        if c == ')':
            p -= 1
            if b == 0: #Not inside a tag
                c = ''
        if c == '<':
            if p == 0: #Not inside parentheses
                b = 1
        if c == '>': #This function will probably fail if the tag is not closed
            b = 0
        if p > b:
            c = ''
        string_out += c
    return string_out

def close():
    if '/wiki/Special:Random' in chain[0]:
        chain.pop(0)
    print("Chain length:", len(chain))
    sys.exit(0)

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == 'random':
            article = 'Special:Random'
        else:
            article = sys.argv[1]
        get_page('/wiki/' + str.replace(article, ' ', '_'))
    else:
        print('No article provided. Getting today\'s featured article.')
        get_featured_article()

if __name__ == '__main__':
    main()
