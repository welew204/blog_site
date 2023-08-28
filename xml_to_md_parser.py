import bs4 as BS
from bs4 import BeautifulSoup
import re
import emoji
from lxml import etree
import datetime as dt

xml_input = '/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/Squarespace-Wordpress-Export-09-21-2022.xml'


def get_root(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    return root


# ------------------from previous parser----------

""" requires input file in XML (no get URL fnc)

on import, this returns a list of blog posts, each blog is a dict:

{
    "title": ...
    "author": ...
    "formatted_content": ...
    "raw_content": ...
    "pubDate": ...
}

"""


inp_xml = '/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/Squarespace-Wordpress-Export-09-21-2022.xml'


def convertXML(file):

    excerpt = "http://wordpress.org/export/1.2/excerpt/"
    content = "http://purl.org/rss/1.0/modules/content/"
    wfw = "http://wellformedweb.org/CommentAPI/"
    dc = "http://purl.org/dc/elements/1.1/"
    wp = "http://wordpress.org/export/1.2/"

    blogs_root = get_root(file)

    blog_list = []

    for item in blogs_root.findall('./channel/item'):

        blog = {}

        for child in item:

            if child.tag == "{http://wordpress.org/export/1.2/}post_type":
                if child.text == "post":
                    cont = item.find(
                        "{http://purl.org/rss/1.0/modules/content/}encoded")
                    tit = item.find("title")
                    if tit.text == None:
                        break
                    date = item.find("pubDate")
                    creator = item.find(
                        "{http://purl.org/dc/elements/1.1/}creator")
                    if "will" in creator.text:
                        author = "WB"
                    elif "hannah" in creator.text:
                        author = "HH"
                    blog["title"] = tit.text
                    blog["author"] = author
                    blog["formatted_content"] = cont.text
                    blog["raw_content"] = just_text(cont.text)
                    blog["pubDate"] = date.text
                    blog_list.append(blog)
                else:
                    break

    return blog_list

some_sample_pathnames = ['Hoj?//w☣️♑️❌🛜tomakethe💩workforyou','CHANGEisintheair!', 'buildasmarterheart', 'BecomingFluent,partI', 'I.Assumptions', 'Howtomakethe💩workforyou']

def clean_string(text):
    clean_text = re.sub(r'[^\w\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F]', '', text)
    emoji_free_text = emoji.replace_emoji(clean_text, '')
    return emoji_free_text

def to_markdown(file_list):
    md_list = []
    new_line_marker = '<br />'
    for post in file_list:
        if post['author'] == 'HH':
            continue
        fixed_date = dt.datetime.strptime(
            post['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
        fixed_date = fixed_date.strftime('%a, %b %d %Y')
        new_ml_post = f"""# {post['title']}
### Author: Will Belew
#### {fixed_date}
---<*>---
{post['raw_content']}
                        """
        new_post = f"# {post['title']}{new_line_marker}"
        new_post += f'Author: Will Belew{new_line_marker}'
        new_post += f"{fixed_date}{new_line_marker}"
        new_post += f"{post['raw_content']}"
        path_title = clean_string(post['title'])
        md_list.append((path_title, new_ml_post))
    return md_list


def save_md_to_file(md_list, target_directory):
    for post in md_list:
        open(f'{target_directory}/{post[0]}.md', 'w+').write(post[1])


def just_text(file):
    # takes out new lines
    no_nlines = re.sub('\n', ' ', file)
    no_bullets = re.sub('\u00a0', ' - ', no_nlines)
    no_nbsp = re.sub("&nbsp;", " ", no_bullets)
    """ soup = unicodedata.normalize("NFKD", soup) """
    # makes a BeautifulSoup object >>> we lose SOME whitespace, especially around punctuation (fixed by passing " " arg to get_text (telling it how to combine individual strings of html))
    soup = BS.BeautifulSoup(no_nbsp, 'html.parser')
    # beautiful soup method that spits out just text >>>>>
    gtext = soup.get_text(" ")
    # takes out bullet points (\xa0) and nbsp (\u00a0) >>> NOT NEEDED??
    # encoding_text = gtext.encode('ascii', 'ignore')
    # get it back to being string (not a byte-string) >>>> NOT NEEDED??
    # final = encoding_text.decode()
    return gtext


"""with open(os.path.join(sys.path[0], inp_xml), 'r') as f:
    data = f.read() """


def main():
    blogs = convertXML(inp_xml)
    md_list = to_markdown(blogs)
    save_md_to_file(md_list, 'content')
    return blogs


if __name__ == "__main__":
    #res = main()
    pass
