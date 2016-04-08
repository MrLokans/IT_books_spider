from flask import Flask, render_template, request
from flask.ext.pymongo import PyMongo
from flask.ext.paginate import Pagination


app = Flask(__name__, static_folder='static')
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'onliner_books'
app.config['POSTS_PER_PAGE'] = 10
mongo = PyMongo(app)


@app.route('/')
def home_page():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    start, end = (page-1) * app.config['POSTS_PER_PAGE'],\
                 (page) * (app.config['POSTS_PER_PAGE'])
    book_posts = mongo.db.books.find()[start:end]
    books_count = mongo.db.books.count()
    pagination = Pagination(page=page, total=books_count,
                            css_framework="bootstrap",
                            search=search, record_name='book_posts',
                            per_page=app.config['POSTS_PER_PAGE'])
    return render_template('books.html',
                           book_posts=book_posts,
                           pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)
