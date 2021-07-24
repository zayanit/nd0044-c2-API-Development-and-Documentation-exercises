import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def get_books(request):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * BOOKS_PER_SHELF
  books = Book.query.order_by(Book.id).limit(BOOKS_PER_SHELF).offset(start)
  books = [book.format() for book in books]
  return books

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
    books = get_books(request)

    if len(books) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'books': books,
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


  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()

      if book is None:
        abort(404)

      book.delete()
      books = get_books(request)

      return jsonify({
        'success': True,
        'deleted': book_id,
        'books': books,
        'total_books': len(Book.query.all())
      })

    except:
      abort(422)

  @app.route('/books', methods=['POST'])
  def create_book():
    body = request.get_json()

    new_title = body.get('title', None)
    new_author = body.get('author', None)
    new_rating = body.get('rating', None)

    try:
      book = Book(title=new_title, author=new_author, rating=new_rating)
      book.insert()

      books = get_books(request)

      return jsonify({
        'success': True,
        'created': book.id,
        'books': books,
        'total_books': len(Book.query.all())
      })

    except:
      abort(422)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422
  
  return app