from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Schema_Movie(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Str()
    director_id = fields.Str()


class Schema_Director_Genre(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = Schema_Movie()
movies_schema = Schema_Movie(many=True)

director_genre_sc = Schema_Director_Genre()
directors_genres_sc = Schema_Director_Genre(many=True)


@movie_ns.route('/')
class GetMovie(Resource):
    def get(self):
        try:
            director_id = request.args.get('director_id')
            genre_id = request.args.get('genre_id')

            if not director_id and not genre_id:
                data = db.session.query(Movie).all()
                for d in data:
                    d.genre_id = d.genre.name
                    d.director_id = d.director.name
                return movies_schema.dump(data), 200

            if director_id and genre_id:
                data = db.session.query(Movie).filter(Movie.director_id == int(director_id),
                                                      Movie.genre_id == int(genre_id)).all()
                return movies_schema.dump(data), 200

            if director_id or genre_id:
                if director_id:
                    data = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
                    return movies_schema.dump(data), 200
                elif genre_id:
                    data = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
                    return movies_schema.dump(data), 200

        except Exception as exc:
            return f'На сервере произошла ошибка "{exc}"', 404

    def post(self):
        try:
            request_json = request.json
            new_mov = Movie(**request_json)
            with db.session.begin():
                db.session.add(new_mov)
            return 'Данные успешно добавлены', 201
        except Exception as exc:
            return f'На сервере произошла ошибка "{exc}"', 404


@movie_ns.route('/<int:uid>')
class GetsMovie(Resource):
    def get(self, uid: int):
        try:
            data = db.session.query(Movie).get(uid)
            return movie_schema.dump(data), 200
        except Exception as exc:
            return str(exc), 404

    def put(self, uid: int):
        try:
            data = db.session.query(Movie).get(uid)
            request_json = request.json

            data.title = request_json.get('title')
            data.description = request_json.get('description')
            data.trailer = request_json.get('trailer')
            data.year = request_json.get('year')
            data.rating = request_json.get('rating')
            data.genre_id = request_json.get('genre_id')
            data.director_id = request_json.get('director_id')

            db.session.add(data)
            db.session.commit()

            return 'Данные обновлены', 204

        except Exception as exc:
            return str(exc), 404

    def delete(self, uid: int):
        try:
            data_delete = db.session.query(Movie).get(uid)
            db.session.delete(data_delete)
            db.session.commit()

            return 'Данные удалены', 204
        except Exception as exc:
            return str(exc), 404


@director_ns.route('/')
class DirectorsReturn(Resource):
    def get(self):
        try:
            data = db.session.query(Director).all()
            return directors_genres_sc.dump(data), 200
        except Exception as exc:
            return str(exc), 404

    def post(self):
        try:
            req_json = request.json
            with db.session.begin():
                db.session.add(Director(**req_json))
            return '', 201
        except Exception as exc:
            return str(exc), 404


@director_ns.route('/<int:uid>')
class Director_uid(Resource):
    def get(self, uid: int):
        try:
            data = db.session.query(Director).get(uid)
            return director_genre_sc.dump(data), 200
        except Exception as exc:
            return str(exc), 404

    def put(self, uid: int):
        try:
            req_json = request.json
            data = db.session.query(Director).get(uid)

            data.name = req_json.get('name')

            db.session.add(data)
            db.session.commit()

            return '', 204
        except Exception as exc:
            return str(exc), 404

    def delete(self, uid: int):
        try:
            data_delete = db.session.query(Director).get(uid)
            db.session.delete(data_delete)
            db.session.commit()

            return '', 204
        except Exception as exc:
            return str(exc), 404


@genre_ns.route('/')
class GenreReturn(Resource):
    def get(self):
        try:
            data = db.session.query(Genre).all()
            return directors_genres_sc.dump(data), 200
        except Exception as exc:
            return str(exc), 404

    def post(self):
        try:
            req_json = request.json
            with db.session.begin():
                db.session.add(Genre(**req_json))
            return '', 201
        except Exception as exc:
            return str(exc), 404


@genre_ns.route('/<int:uid>')
class Genre_uid(Resource):
    def get(self, uid: int):
        try:
            data = db.session.query(Genre).get(uid)
            return director_genre_sc.dump(data), 200
        except Exception as exc:
            return str(exc), 404

    def put(self, uid: int):
        try:
            req_json = request.json
            data = db.session.query(Genre).get(uid)

            data.name = req_json.get('name')

            db.session.add(data)
            db.session.commit()

            return '', 204
        except Exception as exc:
            return str(exc), 404

    def delete(self, uid: int):
        try:
            data_delete = db.session.query(Genre).get(uid)
            db.session.delete(data_delete)
            db.session.commit()

            return '', 204
        except Exception as exc:
            return str(exc), 404


if __name__ == '__main__':
    app.run(debug=True)
