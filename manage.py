# coding:utf-8
from flask_script import Manager

from app.views import app

manager = Manager(app)

@manager.command
def init_db():
    from app.models import Base
    from app.helper import some_engine
    Base.metadata.create_all(some_engine)


@manager.command
def start():
    app.run(host='0.0.0.0', port=8088, debug=False)

if __name__ == "__main__":
    manager.run()