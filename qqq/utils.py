import re

def url_to_html(url):
  """Converts a Youtube url (youtube.com/watch?v=...)
     into a string that can be embedded in html"""
  id = re.search(r'v=([-\w]+)', url)
  if id:
    return r'<iframe width="100%" height="100%" src="http://www.youtube.com/embed/' \
          + id.group(1) + r'" frameborder="0" allowfullscreen></iframe>'
  else:
    return ''
