from app import app, db
from app.models import Admin, Phone


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Admin': Admin, 'Phone': Phone}
