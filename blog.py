import webapp2
import logging
import re
import jinja2
import os
import time
from google.appengine.ext import db

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Blogs(db.Model):
    title = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)#date created


class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def render_blog(self, title="", blog=""):
        blogs =db.GqlQuery("SELECT * FROM Blogs ORDER BY created DESC limit 10")
        self.render("post.html", title=title, blog=blog)

    def get(self):
        logging.info("** MainPage GET")        
        form = JINJA_ENVIRONMENT.get_template('/templates/post.html')
        recent = db.GqlQuery("SELECT * FROM Blogs ORDER BY created DESC limit 10")
        form_vals = {"Blogs": recent, "blank": True}
        self.write(form.render(form_vals))        
        #for blog in recent:
        #    self.write("Title:"+blog.title + "<br>")
        #    self.write("Blog: "+blog.content+"<br>")
        #    self.write("Uploaded: "+blog.created.date().strftime("%a %B %d %Y")+" at "+blog.created.time().strftime("%I:%M:%S %p")+"<br><br><br>")

    def post(self):
        self.write("wot r u doing, theres no post method")

class BlogArchive(MyHandler):
    def get(self, blog_id):
        logging.info("old blog archive")
        logging.info("blog id: %s"%blog_id)
        #self.write("Archive id: %s <br>"%blog_id)
        bloggy = Blogs.get_by_id(int(blog_id))
        form = JINJA_ENVIRONMENT.get_template('/templates/post.html')
        form_vals = {"arch": bloggy}
        self.write(form.render(form_vals))
        #self.write("Title:"+bloggy.title + "<br>")
        #self.write("Blog: "+bloggy.content+"<br>")
        #self.write("Uploaded: "+bloggy.created.date().strftime("%a %B %d %Y")+" at "+bloggy.created.time().strftime("%I:%M:%S %p")+"<br><br><br>")


    def post(self):
        self.write("wot r u doing, theres no post method")

class NewPost(MyHandler):
    def get(self):
        logging.info("*** newpost GET")
        form = JINJA_ENVIRONMENT.get_template('/templates/newpost.html')
        self.write(form.render())

    def post(self):
        logging.info("* post of new post, they have submitted a blog")
        titletemp = self.request.get("subject")
        contenttemp = self.request.get("content")
        blog = Blogs()
        blog.title = titletemp
        blog.content = contenttemp    
        blog.put()
        self.write("title: "+blog.title+" content: "+blog.content)
        time.sleep(0.2)
        self.redirect('/')   

application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'/blog/?', MainPage),
    (r'/blog/newpost/?', NewPost),
    (r'/blog/(\d+)', BlogArchive) # the digits are passed as the id, this is the same as the google datebase ID
], debug=True)
