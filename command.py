import click
import os
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from models import User
from extension import db

@click.command("create-admin")
@with_appcontext
def create_admin():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_phone = os.getenv("ADMIN_PHONE", "0000000000")

    if not admin_email or not admin_password:
        click.echo("Error: ADMIN_EMAIL and ADMIN_PASSWORD environment variables not set")
        return

    admin = User.query.filter_by(email=admin_email).first()
    if admin:
        click.echo("Admin already exists")
        return

    admin = User(
        name="Admin",
        email=admin_email,
        phone=admin_phone,
        password=generate_password_hash(admin_password),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin {admin_email} created successfully!")