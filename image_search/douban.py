import re

from pyquery import PyQuery as pq

from util import urlopen, parse_pair


def parse(url):
    info = {'url': url}
    html = pq(urlopen(url).content)

    # cover image url
    mainpic = html('#mainpic')
    cover_url = mainpic('a').attr('href')
    info['cover_url'] = cover_url
    print cover_url

    # title
    title = mainpic('img').attr('alt')
    info['title'] = title
    print title

    # author, publisher, pub year, price, isbn etc.
    desc = html('#info').html()
    for each in re.split(r'<br/?>', desc):
        each = each.strip()
        if each:
            k, v = parse_pair(pq(each).text())
            info[k] = v
            print u'{} => {}'.format(k, v)

    # tags
    tags = [ pq(a).text() for a in html('#db-tags-section')('a') ]
    info['tags'] = tags
    print ' '.join(tags)
    
    return info
