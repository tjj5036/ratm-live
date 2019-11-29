from flask import (
        Blueprint,
        render_template,
        request)

blueprint = Blueprint('contact', __name__)


@blueprint.route('/contact')
def contact():
    """ Renders the contact page."""
    return render_template("contact.html")
