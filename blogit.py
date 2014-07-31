import os
import re
from string import letters
import webapp2
import jinja2
import time
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__))
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	 autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Bloghandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw) # for non-html data


	def render_str(self, template, **params):
		return render_str(template, **params)


	def render(self, template, **kw):
		self.write(self.render_str(template, **kw)) # gets the template and renders or substitute values with the passsed data(**kw)


def render_post(response, post):###understood
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.content)

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	lastmodified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)


class Postpage(Bloghandler):
	def get(self, post_id):
		key = db.Key.from_path('Post',int(post_id))
		post = db.get(key)

		if not post:
			self.write("bad url link")
			return

		self.render("permalink.html", post = post)

class Newpost(Bloghandler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			p = Post(subject = subject, content = content)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "we need both the title and content"
			self.render("newpost.html", subject = subject, content = content, error = error)
			
class DeletePost(Bloghandler):
	def post(self):
		identity = self.request.get('id')
		key = db.Key.from_path('Post',int(identity))
		post = db.get(key)
		db.delete(post)
		time.sleep(0.5)
		self.redirect('/blog')

### class to display all posts

class Blogfront(Bloghandler): #inherits from bloghnadler class
	def get(self):  #all function should have a self parameter
		posts = db.GqlQuery("select * from Post order by created desc limit 10") # query to look in database and get all blog posts in desc limiting to 10 top posts
		self.render('blogpage.html', posts = posts)


app = webapp2.WSGIApplication([
	('/blog', Blogfront),
	('/blog/newpost', Newpost),
	('/blog/([0-9]+)', Postpage),
	('/blog/delete', DeletePost),	
	],
	debug = True) 