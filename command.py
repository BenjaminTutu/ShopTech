import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from models import User
from extension import db

@click.command("create-admin")
@with_appcontext
def create_admin():
    admin = User.query.filter_by(email="admin@example.com").first()

    if admin:
        click.echo("Admin already exists")
        return

    admin = User(
        name="Admin",
        email="admin@example.com",
        phone="1111100000",
        password=generate_password_hash("admin@123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    click.echo("Admin created successfully")