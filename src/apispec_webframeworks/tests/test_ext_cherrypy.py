# -*- coding: utf-8 -*-
import pytest

from apispec import APISpec
from apispec_webframeworks.cherrypy import CherrypyPlugin

import cherrypy

from .utils import get_paths


@pytest.fixture(params=('2.0', '3.0.0'))
def spec(request):
    return APISpec(
        title='Swagger Petstore',
        version='1.0.0',
        openapi_version=request.param,
        plugins=(CherrypyPlugin(), ),
    )


@pytest.yield_fixture()
def app():
    return cherrypy


class TestPathHelpers:
    def test_path_from_mount(self, app, spec):
        @cherrypy.expose
        class HelloHandler(object):
            @cherrypy.expose
            def test(self):
                return 'hello'

        app.tree.mount(HelloHandler(), '/hello')

        spec.path(
            mount=HelloHandler,
            operations={
                'get': {'parameters': [], 'responses': {'200': {}}},
            },
        )

        paths = get_paths(spec)
        assert '/hello' in paths
        assert 'get' in paths['/hello']
        expected = {'parameters': [], 'responses': {'200': {}}}
        assert paths['/hello']['get'] == expected

    # def test_path_from_method_dispatcher(self, app, spec):
    #     class HelloHandler(object):
    #         def GET(self):
    #             return 'hello'
    #
    #     app.tree.mount(
    #         HelloHandler(), '/hello', config={
    #             '/': {'request.dispatch': app.dispatch.MethodDispatcher()},
    #         },
    #     )
    #
    #     spec.path(
    #         mount=HelloHandler,
    #         operations={
    #             'get': {'parameters': [], 'responses': {'200': {}}}
    #         },
    #     )
    #
    #     paths = get_paths(spec)
    #     assert '/hello' in paths
    #     assert 'get' in paths['/hello']
    #     expected = {'parameters': [], 'responses': {'200': {}}}
    #     assert paths['/hello']['get'] == expected
