from flask import (
        Blueprint,
        render_template,
        request)


blueprint = Blueprint('about', __name__)


@blueprint.route('/about')
def about():
    """ Renders the about page."""
    return render_template("about.html")
