import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(request, allBooks):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * BOOKS_PER_SHELF
  end = start + BOOKS_PER_SHELF
  books = [book.format() for book in allBooks]
  current_books = books[start:end]
  return current_books

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/books')
  def retrieve_books():
    allBooks = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, allBooks)

    if len(current_books) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': len(Book.query.all())
    })

  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_book(book_id):
    body = request.get_json()

    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()

      if book is None:
        abort(404)

      if 'rating' in body:
        book.rating = int(body.get('rating'))
      book.update()

      return jsonify({
        'success': True,
        'id': book.id
      })
      
    except:
      abort(400)


  # @TODO: Write a route that will delete a single book. 
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.


  # @TODO: Write a route that create a new book. 
  #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
  #       Your new book should show up immediately after you submit it at the end of the page. 
  
  return app

    