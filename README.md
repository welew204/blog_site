# Static Site Generator

This is an example of using python with jinja2 templating to build a simple blog site in html and bootstrap. In addition, the post-recommender card on each individual blog post is generated in the backend by NLP processing of the entire blog corpus to score for cosine similarity.

## Env Details

This page was built within a conda virtual env; you can find configuration details in the included environment.yaml file

## Template Format

I created two templates, one for the cover/directory page, and one to generate each individual blog post. They in the /templates directory

## Content Format

Content is stored in markdown format in the /content directory, while rendered html posts are stored in the /posts directory

## Depolyment Details

This site is deploed via GitHub pages, and the live url is [https://welew204.github.io/blog_site/output.html](https://welew204.github.io/blog_site/output.html)
