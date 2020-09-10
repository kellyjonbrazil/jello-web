#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from jello.cli import __version__ as jello_version
from jello.cli import pyquery, load_json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from flask import Flask, render_template, flash, Markup
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


TITLE = 'jello web'
DEBUG = True

app = Flask(__name__)

if os.getenv('APP_KEY'):
    app.config['SECRET_KEY'] = os.getenv('APP_KEY')
    print('Using production key', file=sys.stderr)
else:
    app.config['SECRET_KEY'] = 'deadbeef'
    print('Using development key', file=sys.stderr)


# --- ROUTES ---


@app.route('/', methods=('GET', 'POST'))
def home():
    form = MyInput()
    output = ''
    if form.validate_on_submit():
        try:
            json_input = form.json_input.data
            list_dict_data = load_json(json_input, as_lib=True)
        except Exception as e:
            e_str = str(e).replace('\n', '<br>')
            flash_msg = Markup(f'<p>jello could not read the input. Is it JSON or JSON Lines?<p><strong>{type(e).__name__}:</strong><p>{e_str}')
            flash(flash_msg, 'danger')
            return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)

        try:
            query_input = form.query_input.data
            compact = not form.pretty_print.data
            schema = form.schema.data
            lines = form.lines.data
            output, *_ = pyquery(data=list_dict_data, query=query_input, compact=compact, lines=lines, schema=schema, as_lib=True)
        except Exception as e:
            e_str = str(e).replace('\n', '<br>')
            flash_msg = Markup(f'<p>jello ran into the following exception when running your query:<p><strong>{type(e).__name__}:</strong><p>{e_str}')
            flash(flash_msg, 'danger')
            return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)

        if form.pretty_print.data:
            output = json.dumps(output, indent=2)
        else:
            output = json.dumps(output)
        output = highlight(output, JsonLexer(), HtmlFormatter(noclasses=True))
    return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)


# --- FORMS ---


class MyInput(FlaskForm):
    json_input = TextAreaField('JSON or JSON Lines Input', validators=[DataRequired()])
    query_input = TextAreaField('Jello Query', validators=[DataRequired()])
    pretty_print = BooleanField('Pretty Print', default='checked')
    schema = BooleanField('Print Schema Output')
    lines = BooleanField('Print Lines Output')
    submit = SubmitField('Query JSON')


if __name__ == '__main__':
    # socketio.run(app)
    app.run(debug=DEBUG)
