from pyquery import PyQuery as pq

from bookworm.image_search.util import urlopen, join_url_hostpath, get_url_host


class Ishare(object):

    pattern = 'ishare.iask.sina.com.cn'

    def parse(self, url):
        info = {'url': url}
        html = pq(urlopen(url).content)

        # tilte
        title = html('h1.f14').text()
        info['title'] = title

        # download url
        btn = html('.download_btn_box')
        host = get_url_host(url)
        download_url = join_url_hostpath(host, btn('a').attr('href'))
        info['download_url'] = download_url
        print download_url

        # file size
        file_size = btn('span').text()
        info['file_size'] = file_size
        print file_size

        return info
