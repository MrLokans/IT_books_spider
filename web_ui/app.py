from flask import Flask, render_template, request
from flask.ext.pymongo import PyMongo
from flask.ext.paginate import Pagination


app = Flask(__name__, static_folder='static')
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'onliner_books'
mongo = PyMongo(app)

# TODO: pagination currently does not work


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
    book_posts = mongo.db.books.find()
    books_count = mongo.db.books.count()
    pagination = Pagination(page=page, total=books_count,
                            search=search, record_name='book_posts',
                            per_page=20)
    return render_template('books.html',
                           book_posts=book_posts,
                           pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)
