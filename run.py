from flask_blog import create_app, db, cli
from flask_blog.models import User, Post
from flask_blog.config import Config

app = create_app(Config)
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


if __name__ == "__main__":
    app.run(debug=True, port=1996)
