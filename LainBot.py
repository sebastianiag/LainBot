from argparse import ArgumentParser
import requests
import re
import sqlite3
import simplejson
import time


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
parser = ArgumentParser();
parser.add_argument("--board", type=str, help="chan thread")
parser.add_argument("--output", type=str, help="output directory")
parser.add_argument("--database", type=str, help="database file location")

options = parser.parse_args()


class LainBot:
    
    def __init__(self, board_url, database):
        
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        board = board_url
        catalog_map = dict() # str: thread => list(dict): posts
        link_re = re.compile("(http:+\S+html+)|(https:+\S+html+)|(ftp:+\S+)", re.IGNORECASE)
        magnet_re = re.compile("magnet:+\S+", re.IGNORECASE)

    def post_processer(self, posts):
        file_location = ("https://lainchan.org/%CE%BB/src/").encode("utf-8")
        for post in posts:
            body_processer(post['com'])
            try:
                filename = post['filename'] + post['ext']
                file_timestamp = post['tim']
                file_buffer = requests.get(file_location+file_timestamp+post['ext'], headers=HEADERS, stream=True)
                if file_buffer.ok:
                    cur.execute("INSERT INTO resource(filename, location) VALUES('%s', '%s')" %(filename, file_location+file_timestamp+post['ext']))
                    with open(options.output+"/"+filename, 'wb') as out_file:
                        print "Downloading %s at %s" % (filename, file_location+file_timestamp+post['ext'])
                        for block in file_buffer.iter_content(1024):
                            out_file.write(block)
                else:
                    print "file %s at %s could not be downloaded" % (filename, file_location+file_timestamp+post['ext'])
                    continue
            except KeyError:
                print "No file found in this post. Moving on..."
                continue
        conn.commit()
        print "Finished!"
        return
    
        
    def thread_getter(self):
        response = requests.get(board, header=HEADERS)
        if not response.ok:
            print "Could not get catalog. Abort"
            return

        catalog_object = simplejson.loads((response.text).encode("utf-8"))
        thread_list = list()
        for x in catalog_object:
            thread_list += x['threads']
        thread_links = ["https://lainchan.org/λ/res/%s.json" % (str(i['no'])) for i in thread_list]
        for thread_link in thread_links:
            response = requests.get(thread_link, headers=HEADERS)
            posts = simplejson.loads((response.text).encode("utf-8"))['posts']
            try:
                catalog_map[posts[0]['sub']] = posts
            except KeyError:
                catalog_map[posts[0]['no']] = posts
        return

    def body_processer(self, body):
        cur.execute("INSERT INTO posts(body, no) VALUES('%s', '%s')" %(post['com'], post['no']))
        for link in link_re.findall(body):
            link = ''.join(link)
            print "Pushing link to database"
            cur.execute("INSERT INTO links(link) VALUES('%s')" %(link))

        for torrent in magnet_re.findall(body):
            print "Pushing magnet link: %s" % (torrent)
            cur.execute("INSERT INTO torrents(magnet) VALUES('%s')" %(torrent))
        
        return
        
    def run_bot(self):
        while True:
            thread_getter()
            for thread in catalog_map:
                post_processer(catalog_map[thread])
            time.sleep(1800)
        conn.close()

def main():
    lain_bot = LainBot(options.board, options.database)
    lain_bot.run_bot()

if __name__ == '__main__':
    main()

