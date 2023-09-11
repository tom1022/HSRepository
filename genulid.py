import ulid
from dbapp import db, app
from dbapp.models.tables import PAGES

with app.app_context():
    allpages = PAGES.query.all()

    for page in allpages:
        if page.ulid is None:
            page.ulid = ulid.new().str
            db.session.add(page)
            db.session.commit()
