import time
from base import BaseHandler
from lib import *

class IdeaListHandler(BaseHandler):
    def get(self):
        ideas=self.db['Idea'].find().sort('date',-1).limit(9)
        ceshi=self.db['user'].find_one({'username':'lowstz'})
        self.render("idea.html",ideas=ideas)
#        self.flash_message('Please fill the required fields', 'error')
    def post(self):
        tex1=self.get_argument("tef")
        tex2=self.get_argument("tes")
        self.render("topic.html",page_title=tex1,header_text=tex2)

#        t=self.db['user'].update({'user':'sw78'},{"$push":{"comments":{"time":tex1,"xx":tex2}}})

class NewIdeaHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.render('new_idea.html')
        else:
            self.flash("请先登陆后再进行操作", "error")
            self.redirect('/account/signin')
    def post(self):
        title=self.get_argument("title",None)
        content_md=self.get_argument("content",None)
        content=md_to_html(content_md)
        if not (title and content_md):
#            self.flash_message('请输入标题和正文！', 'error')
            self.render('new_idea.html')
            return
        iid = self.db.auto_inc.find_and_modify(update={"$inc":{"idea_id":1}},
                                                query={"name":"idea_id"}, new=True).get("idea_id")
        self.db['Idea'].save({'author':self.get_current_user(),'date':time.time(),'title':title,
                                'text':content, "click" :0, "iid" : iid})
        self.redirect("/idea")
        
        
class IdeaHanler(BaseHandler):
    def get(self, iid=None):
        iid=int(iid)
        idea=self.db['Idea'].find_one({"iid":iid})
        self.render('text_idea.html',idea=idea)
    def post(self, iid):
#        iid=self.get_argument("idea['iid']", None)
        content=self.get_argument('content', None)
#        if not content:
#            self.flash_message('请输入标题和正文！', 'error')
#            self.render('new_idea.html')
#            return
        self.db['reply_Idea'].save({"content" : content, "author" :self.get_current_user(), 
                                    "time" : time.time(), "iid" :iid })
        url = "/idea/" + iid
        self.redirect(url)
        
        
handlers = [
    (r'/idea',IdeaListHandler),
    (r'/idea/new_idea',NewIdeaHandler),
    (r'/idea/(\w+)',IdeaHanler),
]
