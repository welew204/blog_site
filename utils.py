import sys
print("Executing from:", sys.executable)

from jinja2 import Template
import os
import markdown
# has metadata standard (a few different formats) ie: "markdown frontmatter"
# look at HW for standardized (maybe '---' ?)
# "decap" CMS by netlify
from xml_to_md_parser import clean_string
from datetime import datetime as dt
import nltk
import pprint
import numpy as np


# xml_parser that takes in xml, parses, and returns list of md files
# then, builds those into individual md files in '/content'
# for now some fake data...
fake_blogs = [
    ["That One About Beaks", """Flapdoodle zephyrizes through the whizzing
     wobbleberries, shimmering in kaleidoscopic splendor. Squiggly wobblefins
     dance a jig while giggling moonbeams serenade the sprockets. Jumbled
     fizzlefluff mingles with zany zorbits, creating a whimsical symphony
     of zibber-zabber that tickles the senses and frolics in the nonsensical nebula."""],
    ["Friendly Ogres", """Flapdoodle zephyrizes through the whizzing
     wobbleberries, shimmering in kaleidoscopic splendor. Squiggly wobblefins
     dance a jig while giggling moonbeams serenade the sprockets. Jumbled
     fizzlefluff mingles with zany zorbits, creating a whimsical symphony
     of zibber-zabber that tickles the senses and frolics in the nonsensical nebula."""],
    ["Funicular Barbarism", """Flapdoodle zephyrizes through the whizzing
     wobbleberries, shimmering in kaleidoscopic splendor. Squiggly wobblefins
     dance a jig while giggling moonbeams serenade the sprockets. Jumbled
     fizzlefluff mingles with zany zorbits, creating a whimsical symphony
     of zibber-zabber that tickles the senses and frolics in the nonsensical nebula."""],
]
# function that grabs md from each md file in '/content', processes into
# list of 'blogs' each (1. Title, 2. Content, 3. straight html (from markdown)) ... for now :>)


def harvest_posts(directory):
    blogs_list = []
    for file in os.listdir(directory):
        with open(os.path.join(directory, file), encoding="utf-8") as f:
            post_string = f.read()
            jt_index = post_string.find('\n\n')
            just_text = post_string[jt_index:]
            post_md = markdown.Markdown(extensions=['meta'])
            post_md_html = post_md.convert(post_string)
            if 'Untitled' in post_md.Meta['title'][0]:
                continue
            
            path_title = clean_string(post_md.Meta['title'][0])
            res = {'post_title': post_md.Meta['title'][0],
                   'post_author': post_md.Meta['authors'][0],
                   'post_date': post_md.Meta['date'][0],
                   'post_html': post_md_html,
                   'post_content': just_text,
                   'path_title': path_title}
            blogs_list.append(res)
    return blogs_list


# build site_html with jinja2 Template (get template string from '/templates')
# save this as a new html file that is ... hosted on github?


def build(title, byline):
    blogs_list = harvest_posts('content/')
    sim_matrix = build_similarity_matrix(blogs_list)
    with open('templates/cover_page_template.html') as cover_page_template_string:
        template_string = cover_page_template_string.read()
        cover_template = Template(template_string)
    with open('templates/blog_page_template.html') as post_page_template_string:
        template_string = post_page_template_string.read()
        post_template = Template(template_string)

    current_library_settings = {
        'blog_title': title,
        'byline': byline,
        'blogs': blogs_list
    }

    summary_result = cover_template.render(current_library_settings)

    # Write the resulting HTML to a new file
    open('output.html', 'w+').write(summary_result)

    for i, post in enumerate(blogs_list):
        # previous method using jinja2, but now using markdown library to go straight from MD to html :)

        post['blog_title'] = title
        """ post['path_title'] = ''.join(
            filter(check_for_punc_in_string, post['post_title'].split())) """
        post['byline'] = byline
        # just the top 5 blogs
        sim_blogs = sim_matrix[post['post_title']][:5]
        prepped_sim_blogs = [{"title": post[0], "path": clean_string(post[0])+".html"} for post in sim_blogs]
        post['sim_posts'] = prepped_sim_blogs
        post_result = post_template.render(post)

        open(f'posts/{post["path_title"]}.html', 'w+').write(post_result)


def new(title=""):
    directory = 'content/'
    untitleds = []
    today = dt.now().strftime('%a, %b %d %Y')
    if title == "":
        # then I want to hunt for other untitleds, to see how to number this new one
        for file in os.listdir(directory):
            if "Untitled" in file:
                trimmed_file = file[:-3]
                untitleds.append(trimmed_file)
        if untitleds == []:
            untitled_string = "Untitled1"
        else:
            untitleds.sort()
            next_untitled = str(int(untitleds[-1][8:]) + 1)
            untitled_string = "Untitled"+next_untitled
        title = untitled_string
    new_blog = f'''Title:   {title}
Summary: 
Authors: {"Will Belew"}
Date:    {today}

'''
    path_title = clean_string(title) + ".md"
    with open(os.path.join(directory, path_title), "x") as f:
        f.write(new_blog)

def cosine_similarity(vec1, vec2):
    new_vector_size = max(len(vec1), len(vec2))
    vec1_copy = vec1.copy()
    vec2_copy = vec2.copy()
    vec1_copy.resize(new_vector_size, refcheck=False)
    vec2_copy.resize(new_vector_size, refcheck=False)
    dot_product = np.dot(vec1_copy, vec2_copy)
    magnitude = np.linalg.norm(vec1_copy)*np.linalg.norm(vec2_copy)
    if magnitude == 0:
        # is this a good stand in? ie is '0' a good final cosine-similarity if either vector == 0?
        return 0
    return dot_product / magnitude

def build_similarity_matrix(blogs_list):
    """takes as input a list of texts (blogs), and returns a 'similarity_matrix' dictionary in format:
    {title}: [similar titles in order of descending similarity]"""
    blog_posts = {post['post_title']: post['post_content'] for post in blogs_list if 'Untitled' not in post['post_title']}
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    stemmer = nltk.PorterStemmer()
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # this takes out ~180 overly-common words
    preprocessed_posts = {}
    for title, post in blog_posts.items():
        tokens = tokenizer.tokenize(post.lower())
        filtered_tokens = [word for word in tokens if word not in stop_words]
        stems = [stemmer.stem(token) for token in filtered_tokens]
        preprocessed_posts[title] = stems
    # Create a TextCollection for TF-IDF calculations
    texts = nltk.TextCollection(preprocessed_posts.values())

    # Calculate TF-IDF scores
    tfidf_scores = {}
    for title, post in preprocessed_posts.items():
        tfidf_scores[title] = {term: texts.tf_idf(term, post) for term in post}
    similarity_matrix = {}
    for title, stemmed_post in tfidf_scores.items():
        similarity_matrix[title] = {}
        for title2, stemmed_post2 in tfidf_scores.items():
            if title == title2:
                continue
            post_1_vector = np.array(list(stemmed_post.values()))
            post_2_vector = np.array(list(stemmed_post2.values()))
            post_similarity = cosine_similarity(post_1_vector, post_2_vector)
            similarity_matrix[title][title2] = post_similarity
        similarity_matrix[title] = sorted(similarity_matrix[title].items(), key = lambda x: x[1], reverse=True)
        # pprint.pprint(similarity_matrix[title])
    return similarity_matrix

def main():
    build('Soul Compost',
          '...creative garbage that sometimes grows flowers.')


if __name__ == "__main__":
    #new()
    main()
