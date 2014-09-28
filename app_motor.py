#coding=utf-8
import os.path
import torndb
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import markdown
from tornado import escape
from tornado import gen
from tornado.web import asynchronous
from tornado.options import define, options
from datetime import datetime
from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient
from your_local_settings import *
import motor
import pymongo

pymongo_db = pymongo.MongoClient().mydatabase

def mult_div(com_id, com_dict={}, com_sum=0, coms_list=[]):            
    head_str = '<div class="comment">'    
    if not pymongo_db.comments.find_one({"id":com_id}):
        return com_dict
    else:            
        coms = pymongo_db.comments.find_one({"id":com_id})    
        com_sum = com_sum + 1
        coms_list.insert(0, coms)        
        key = head_str * com_sum
        com_dict = {}
        com_dict[key] = coms_list
        if not coms['quote_who']:
            return com_dict
        else:
            com_id = int(coms['quote_who'])
            return mult_div(com_id, com_dict, com_sum, coms_list)


class DbHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def pymongo_db(self):
        return self.application.pymongo_db

    @gen.coroutine
    def auto_gen_id(self):
        cursor = self.db.comments.find({}, {"id":1, "_id":0}).sort("id", pymongo.DESCENDING)
        id = cursor.to_list(length=1)
        raise gen.Return(id)

    @gen.coroutine
    def post_doc(self, doc):
        f = self.db.comments.insert(doc)
        raise gen.Return(f)

    @gen.coroutine
    def generate_coms(self):
        comments = yield self.db.comments.find().sort("id", pymongo.DESCENDING).to_list(length=50)
        def f(self):
            for i in comments:
                yield mult_div(i['id'], {}, 0, [])
        coms_list = f(self)
        raise gen.Return(coms_list)

    @gen.coroutine
    def get(self):        
        coms_list = yield self.generate_coms()
        self.render("index_motor.html", coms_list=coms_list)

    @gen.coroutine
    def post(self):
        last_id = (yield self.auto_gen_id())
        if last_id:
            try:
                id =(yield last_id)[0]["id"]
                id = id + 1
            except:
                id = 1
        comment_id = id
        author = self.get_argument('author')
        quote_who = int(self.get_argument('quote_who'))
        comment = escape.xhtml_escape(self.get_argument('comment'))
        doc = {
        "id":comment_id,
        "quote_who":quote_who,
        "author":author,
        "created_time":datetime.now(),
        "comment":comment
        }
        yield self.post_doc(doc)
        self.redirect('/')


define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", DbHandler),
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
        self.db = motor.MotorClient().mydatabase
        self.pymongo_db = pymongo.MongoClient().mydatabase

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
