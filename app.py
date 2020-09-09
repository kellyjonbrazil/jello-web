#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from jello import cli
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SelectField, BooleanField, SubmitField
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
            parser = importlib.import_module('jc.parsers.' + form.command_parser.data)
            output = parser.parse(form.command_output.data, quiet=True)
        except Exception:
            flash('jc was unable to parse the content. Did you use the correct parser?', 'danger')
            return redirect(url_for('home'))
        if form.pretty_print.data:
            output = json.dumps(output, indent=2)
        else:
            output = json.dumps(output)
        output = highlight(output, JsonLexer(), HtmlFormatter(noclasses=True))
    return render_template('home.html', title=TITLE, jc_info=jc_info, form=form, output=output)


# --- FORMS ---


class MyInput(FlaskForm):
    command_parser = SelectField('Parser', choices=parser_mod_list)
    command_output = TextAreaField('Command Output', validators=[DataRequired()])
    pretty_print = BooleanField('Pretty Print', default='checked')
    submit = SubmitField('Convert to JSON')


if __name__ == '__main__':
    app.run(debug=DEBUG)
