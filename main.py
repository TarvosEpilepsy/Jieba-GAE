#!/usr/bin/env python
#
import os
import webapp2
import logging

ALLOWED_APP_IDS = ('24ae7c', '2b359e')
from google.appengine.api import memcache
import hashlib
import json

MEMCACHE_TIMEOUT = 60 * 60 * 24


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class Analyse(webapp2.RequestHandler):
    def handle_requests(self):

        # app_id = self.request.headers.get('X-Appengine-Inbound-Appid', None)
        # logging.info("APPID:%s" % app_id)
        # if app_id in ALLOWED_APP_IDS:
        #     pass
        # else:
        #     self.abort(403)


        text = self.request.get("text", default_value="")
        withWeight = int(self.request.get("withWeight", default_value="0"))
        mode = self.request.get("mode", default_value="")
        topK = int(self.request.get("topK", default_value="20"))
        allowPOS = tuple(self.request.get_all("allowPOS"))
        md5sum = hashlib.md5((''.join(allowPOS) + text + mode + str(withWeight) + str(topK)).encode("utf-8")).hexdigest()

        json_data = memcache.get('{}:Analyse'.format(md5sum))
        if json_data is None:
            # import jieba.analyse

            # jieba.analyse.set_stop_words(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stop_words.txt'))

            # jieba.dt.tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')

            data = {'text': text, 'mode': mode, 'topK': topK, 'allowPOS': allowPOS, 'md5sum': md5sum}

            if mode == "TF-IDF":
                import jieba.analyse.tfidf
                jieba.dt.tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
                default_tfidf = jieba.analyse.tfidf.TFIDF()
                extract_tags = default_tfidf.extract_tags
                default_tfidf.set_stop_words(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stop_words.txt'))
                set_idf_path = default_tfidf.set_idf_path
                data["result"] = extract_tags(text, topK=topK, withWeight=bool(withWeight),
                                                            allowPOS=allowPOS)
            else:
                import jieba.analyse.textrank
                jieba.dt.tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
                default_textrank = jieba.analyse.textrank.TextRank()
                textrank = default_textrank.extract_tags
                default_textrank.set_stop_words(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stop_words.txt'))
                data["result"] = textrank(text, withWeight=bool(withWeight), topK=topK)

            json_data = json.dumps(data)
            memcache.add('{}:Analyse'.format(md5sum), json_data, MEMCACHE_TIMEOUT)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json_data)


    def get(self):
        self.handle_requests()

    def post(self):
        self.handle_requests()


class Cut(webapp2.RequestHandler):
    def handle_requests(self):

        # app_id = self.request.headers.get('X-Appengine-Inbound-Appid', None)
        # logging.info("APPID:%s" % app_id)
        # if app_id in ALLOWED_APP_IDS:
        #     pass
        # else:
        #     self.abort(403)

        text = self.request.get("text", default_value="")
        mode = int(self.request.get("cut_all", default_value=""))
        md5sum = hashlib.md5((text + str(mode)).encode("utf-8")).hexdigest()

        json_data = memcache.get('{}:Cut'.format(md5sum))
        if json_data is None:
            import jieba

            jieba.dt.tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')

            data = {'text': text, 'mode': mode, 'md5sum': md5sum}
            data["result"] = []

            for x in jieba.cut(text, cut_all=bool(mode)):
                data["result"].append(x)

            json_data = json.dumps(data)
            memcache.add('{}:Cut'.format(md5sum), json_data, MEMCACHE_TIMEOUT)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json_data)

    def get(self):
        self.handle_requests()

    def post(self):
        self.handle_requests()


app = webapp2.WSGIApplication([('/cut', Cut),
                               ('/analyse', Analyse)], debug=True)