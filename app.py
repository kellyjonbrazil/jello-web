#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from jello import __version__ as jello_version
from jello.lib import opts, load_json, pyquery, Schema, Json
from flask import Flask, render_template, flash, Markup
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


TITLE = 'jello web'
DEBUG = False

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
            list_dict_data = load_json(json_input)
        except Exception as e:
            e_str = str(e).replace('\n', '<br>')
            flash_msg = Markup(f'<p>Jello could not read the input. Is it JSON or JSON Lines?<p><strong>{type(e).__name__}:</strong><p>{e_str}')
            flash(flash_msg, 'danger')
            return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)

        try:
            query_input = form.query_input.data
            opts.schema = form.schema.data
            opts.types = form.types.data
            opts.compact = form.compact.data
            opts.lines = form.lines.data
            response = pyquery(list_dict_data, query_input)

            if opts.schema:
                schema = Schema()
                output = schema.create_schema(response)
                output = schema.html_output(output)
            else:
                json_out = Json()
                output = json_out.create_json(response)
                output = json_out.html_output(output)

        except Exception as e:
            e_str = str(e).replace('\n', '<br>')
            flash_msg = Markup(f'<p>Jello ran into the following exception when running your query:<p><strong>{type(e).__name__}:</strong><p>{e_str}')
            flash(flash_msg, 'danger')
            return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)

    return render_template('home.html', title=TITLE, jello_version=jello_version, form=form, output=output)


# --- FORMS ---


class MyInput(FlaskForm):
    json_input = TextAreaField('JSON or JSON Lines Input', validators=[DataRequired()],
                               default='{"foo": {"bar": [1, 2, 3]}}')
    query_input = TextAreaField('Jello Query', validators=[DataRequired()],
                                default='_.foo')
    compact = BooleanField('Compact Output')
    schema = BooleanField('Schema Output')
    types = BooleanField('Schema Type Annotations')
    lines = BooleanField('Lines Output')
    submit = SubmitField('Query JSON')


if __name__ == '__main__':
    # socketio.run(app)
    app.run(debug=DEBUG)
