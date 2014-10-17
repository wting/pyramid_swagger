import pytest
import simplejson


@pytest.fixture
def test_app(**overrides):
    """Fixture for setting up a test test_app with particular settings."""
    from .app import main
    from webtest import TestApp
    settings = dict({
        'pyramid_swagger.schema_directory': 'tests/sample_schemas/good_app/',
        'pyramid_swagger.enable_response_validation': False,
        'pyramid_swagger.enable_swagger_spec_validation': False},
        **overrides
    )
    return TestApp(main({}, **settings))


def test_422_if_required_query_args_absent(test_app):
    assert test_app.get(
        '/sample/path_arg1/resource',
        expect_errors=True,
    ).status_code == 422


def test_200_if_optional_query_args_absent(test_app):
    assert test_app.get(
        '/sample/path_arg1/resource',
        params={'required_arg': 'test'},  # no `optional_arg` arg
    ).status_code == 200


def test_200_if_request_arg_is_wrong_type(test_app):
    assert test_app.get(
        '/sample/path_arg1/resource',
        params={'required_arg': 1.0},
    ).status_code == 200


def test_200_if_request_arg_types_are_not_strings(test_app):
    assert test_app.get(
        '/get_with_non_string_query_args',
        params={
            'int_arg': '5',
            'float_arg': '3.14',
            'boolean_arg': 'true',
        },
    ).status_code == 200


def test_404_if_path_not_in_swagger(test_app):
    assert test_app.get(
        '/does_not_exist',
        expect_errors=True,
    ).status_code == 404


def test_422_if_request_arg_is_wrong_type_but_not_castable(test_app):
    assert test_app.get(
        '/get_with_non_string_query_args',
        params={'float_arg': 'foobar'},
        expect_errors=True,
    ).status_code == 422


def test_422_if_path_arg_is_wrong_type(test_app):
    assert test_app.get(
        '/sample/invalid_arg/resource',
        params={'required_arg': 'test'},
        expect_errors=True,
    ).status_code == 422


def test_200_if_path_arg_is_wrong_type_but_castable(test_app):
    assert test_app.get(
        '/sample/nonstring/3/1.4/false',
    ).status_code == 200


def test_422_if_required_body_is_missing(test_app):
    assert test_app.post_json(
        '/sample',
        {},
        expect_errors=True,
    ).status_code == 422


def test_200_on_json_body_without_contenttype_header(test_app):
    """See https://github.com/striglia/pyramid_swagger/issues/49."""
    # We use .post to avoid sending a Content Type of application/json.
    assert test_app.post(
        '/sample?optional_string=bar',
        simplejson.dumps({'foo': 'test'}),
    ).status_code == 200


def test_422_if_body_has_missing_required_arg(test_app):
    assert test_app.post_json(
        '/sample',
        {'bar': 'test'},
        expect_errors=True,
    ).status_code == 422


def test_200_if_body_has_missing_optional_arg(test_app):
    assert test_app.post_json(
        '/sample',
        {'foo': 'test'},
    ).status_code == 200


def test_200_if_required_body_is_model(test_app):
    assert test_app.post_json(
        '/sample',
        {'foo': 'test', 'bar': 'test'},
    ).status_code == 200


def test_200_if_required_body_is_primitives(test_app):
    assert test_app.post_json(
        '/post_with_primitive_body',
        ['foo', 'bar'],
    ).status_code == 200


def test_422_if_extra_body_args(test_app):
    assert test_app.post_json(
        '/sample_post',
        {'foo': 'test', 'bar': 'test', 'made_up_argument': 1},
        expect_errors=True,
    ).status_code == 422


def test_422_if_extra_query_args(test_app):
    assert test_app.get(
        '/sample/path_arg1/resource?made_up_argument=1',
        expect_errors=True,
    ).status_code == 422


def test_200_skip_validation_with_wrong_path():
    assert test_app(**{'pyramid_swagger.skip_validation': ['/(sample)\\b']}) \
        .get('/sample/test_request/resource') \
        .status_code == 200
