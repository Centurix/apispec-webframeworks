# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

import cherrypy

from apispec import BasePlugin, yaml_utils
from apispec.exceptions import APISpecError


RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


class CherrypyPlugin(BasePlugin):
    """APISpec plugin for Cherrypy"""

    @staticmethod
    def cherrypypath2openapi(path):
        """Convert a CherryPy URL rule to an OpenAPI-compliant path.

        :param str path: CherryPy path template.
        """
        return RE_URL.sub(r'{\1}', path)

    @staticmethod
    def _app_for_mount(mount, app=None):
        """
        Find the matching application in the CherryPy tree

        :param object mount: Tree mounted object
        :return: object
        """
        if app is None:
            app = cherrypy

        for application in app.tree.apps:
            if isinstance(app.tree.apps[application].root, mount):
                return app.tree.apps[application]

        raise APISpecError('Could not find endpoint for mount')

    def path_helper(self, operations, mount, app=None, **kwargs):
        """
        Find exposed methods in the CherryPy tree objects either by
        MethodDispatcher type definitions, or by @expose decorators

        :param operations: Mutable operations dictionary
        :param mount: CherryPy tree object
        :param app:
        :param kwargs:
        :return: Path to the tree object
        """
        application = self._app_for_mount(mount, app)
        if isinstance(application.config['/']['request.dispatch'], cherrypy.dispatch.MethodDispatcher):
            # Look for HTTP methods by method name
            for method in dir(application.root):
                if method in ['GET', 'DELETE', 'PATCH', 'POST', 'PUT']:
                    http_method = getattr(application.root, method)
                    operations.update(yaml_utils.load_operations_from_docstring(http_method.__doc__))

        # Now look for @expose methods
        for method in dir(application.root):
            http_method = getattr(application.root, method)
            if hasattr(http_method, 'exposed') and http_method.exposed:
                operations.update(yaml_utils.load_operations_from_docstring(http_method.__doc__))

        operations.update(yaml_utils.load_operations_from_docstring(mount.__doc__))
        return CherrypyPlugin.cherrypypath2openapi(application.script_name)
