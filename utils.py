from jinja2 import Template
import os
import markdown
from xml_to_md_parser import check_for_punc_in_string
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
        with open(os.path.join(directory, file)) as f:
            post_string = f.read()
            title_end_index = post_string.find('\n')
            post_title = post_string[2:title_end_index]
            content_start_index = post_string.find('---<*>---')
            post_content = post_string[content_start_index+10:]
            post_html = markdown.markdown(post_string)
            path_title = ''.join(
                filter(check_for_punc_in_string, post_title.split()))
            res = {'post_title': post_title,
                   'post_content': post_content,
                   'post_html': post_html,
                   'path_title': path_title}
            blogs_list.append(res)
    return blogs_list


# build site_html with jinja2 Template (get template string from '/templates')
# save this as a new html file that is ... hosted on github?


def build(blogs_list, title, byline):
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
        post_result = post_template.render(post)

        open(f'posts/{post["path_title"]}.html', 'w+').write(post_result)


def main():
    content_dir = 'content/'
    blogs_from_content = harvest_posts(content_dir)
    build(blogs_from_content, 'Soul Compost',
          '...creative garbage that sometimes grows flowers.')


if __name__ == "__main__":
    main()
