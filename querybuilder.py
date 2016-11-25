# -*- coding: utf-8 -*-

"""This module contains a SQL Template & Parameterization utility."""

import re

import jinja2


class QueryBuilder(object):
    """Basic Query Template Renderer utilizing the Jinja2 engine.

    Parameters
    ----------
    statements : str
        String template of sql statements to render.
    prefix : str, optional (default=None)
        String to prefix to each query, typically a filename.

    Attributes
    ----------
    original : str
        Original template of sql statements.
    prefix : str
        String to prefix to each query, typically a filename.
    template : object <jinja2.Template>
        Templated jinja2 object of given `statements`.

    Methods
    -------
    render(params={})
        Render prepared statements w/ parameter injection.

    Examples
    --------
    >>> statement = 'select * from {{table}} where date = "{{date}}"'
    >>> params = {'table': 'test', 'date': '2016-11-23'}
    >>> rendered = QueryBuilder(statement).render(params)
    >>> rendered
    select * from test where day = "2016-11-23"

    >>> statements = '''
    >>> {% for date in dates %}
    >>> select * from {{table}} where day = "{{date}}"
    >>> {% endfor %}
    >>> '''
    >>> params = {
    >>>     'table': 'test',
    >>>     'dates': ['2016-11-21', '2016-11-22', '2016-11-23']
    >>> }
    >>> rendered = QueryBuilder(statements).render(params)
    >>> rendered
    select * from test where day = "2016-11-21"
    select * from test where day = "2016-11-22"
    select * from test where day = "2016-11-23"

    Notes
    -----
    - This is purely a string (sql) builder, and in no way validates output.

    """

    def __init__(self, statements, prefix=None):
        self.original = statements
        self.prefix = prefix or type(self).__name__
        self.template = jinja2.Template(statements)

    def render(self, params=None):
        """Render & prepare statements w/ parameter injection.

        Parameters
        ----------
        params : array-like <dict>, optional (default=None)
            Dictionary of parameters for template injection.

        Returns
        -------
        statements : array-like <list>
            Parameterized list of sql statements.

        Raises
        ------
        TypeError
            If given params is not None or 'dict'.

        """
        if params is None:
            params = dict()

        if not isinstance(params, dict):
            msg = 'Provided `params` is not dict (type=%s)' % type(params)
            raise TypeError(msg)

        rendered = self.template.render(params)

        # Remove multiline comments (ie. /*...*/)
        rendered = re.sub(r'\/[*][^*]*?[*]\/', '', rendered, flags=re.M)
        # Remove singleline comments (ie -- or #)
        rendered = re.sub(r'(--|#).*?\n', '', rendered)
        # Split queries on semicolons
        rendered = rendered.split(';')

        statements, stmt = [], '-- %s (#%s) --\n%s\n'
        for index, statement in enumerate(rendered):
            statement = statement.strip()

            if statement:
                statement = stmt % (self.prefix, index+1, statement)
                statements.append(statement)

        return statements


if __name__ == '__main__':

    import codecs
    import os


    def load_template_statements(filename):
        """Load file contents (statements) from this directory.

        Parameters
        ----------
        filename : str
            Filename of statements file in this directory.

        Returns
        -------
        statements : str
            Loaded statements from given `filename`.

        """
        here = os.path.dirname(os.path.abspath(__file__))
        sqlfile = os.path.join(here, filename)

        with codecs.open(sqlfile, 'r') as infile:
            statements = infile.read()

        return statements

    filename = 'example.sql'
    statements = load_template_statements(filename)

    params = {'dates': ['2016-11-21', '2016-11-22', '2015-11-23']}
    params['start_date'] = min(params['dates'])
    params['end_date'] = max(params['dates'])
    params['test'] = 'testing_unused_param'

    rendered = QueryBuilder(statements, prefix=filename).render(params)

    for index, statement in enumerate(rendered):
        print(statement)
