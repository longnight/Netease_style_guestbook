#coding=utf-8

import os.path
import torndb
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
from tornado import gen
from tornado.web import asynchronous
from tornado.options import define, options
from datetime import datetime
from your_local_settings import *

class IndexHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    # @gen.coroutine
    def get(self):
        comments = self.db.query(
            "SELECT * FROM netease_style_guestbook"
            " ORDER BY created_time DESC LIMIT 50")
        coms_list = []
        for i in comments:
            div_coms = mult_div(i['id'], {}, 0, [])
            coms_list.append(div_coms)

        self.render("index.html", coms_list = coms_list)

    def post(self):
        author = self.get_argument('author')
        print author
        quote_who = self.get_argument('quote_who')
        comment = escape.xhtml_escape(self.get_argument('comment').replace("%", "%%"))
        sql = '''
            INSERT INTO `netease_style_guestbook`
            SET 
            created_time=\'%s\',
            comment=\'%s\',
            author=\'%s\'
            ''' % (datetime.now(),comment, author)
        if quote_who:
            sql += ",quote_who=\'%s\'" % quote_who
        sql += ";"
        self.db.execute(sql)
        self.redirect('/')

        
# @gen.coroutine
def mult_div(com_id, com_dict={}, com_sum=0, coms_list=[]):
    db = torndb.Connection(
        host=options.mysql_host, database=options.mysql_database,
        user=options.mysql_user, password=options.mysql_password)
    head_str = '<div class="comment">'    
    if not db.get("SELECT * FROM `netease_style_guestbook` WHERE `id`= %s" % com_id):
        return com_dict
    else:
        coms = db.get("SELECT * FROM `netease_style_guestbook` WHERE `id`= %s" % com_id)
        com_sum = com_sum + 1
        coms_list.insert(0, coms)        
        key = head_str * com_sum
        com_dict = {}
        com_dict[key] = coms_list
        if not coms['quote_who']:
            return com_dict
        else:
            com_id = coms['quote_who']
            return mult_div(com_id, com_dict, com_sum, coms_list)


        
define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="blog database host")
define("mysql_database", default=db_name, help="database name")
define("mysql_user", default=db_user, help="database user")
define("mysql_password", default=db_pw, help="database password")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
        ]
        settings = dict(
            blog_title=u"My guestbook",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()