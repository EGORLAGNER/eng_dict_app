import pytest

from contextlib import nullcontext as does_not_raise

from core.services.excel_import.main import _check_value_is_bool, _check_value_is_string


# (4, [], 4, int, pytest.raises(TypeError)),


class TestMain:
    @pytest.mark.parametrize(
        'value, expected_result, expected_type, expectations',
        [

            ('', False, bool, does_not_raise()),
            (2, False, bool, does_not_raise()),
            (True, True, bool, does_not_raise()),
            (False, True, bool, does_not_raise()),

        ]
    )
    def test_check_value_is_bool(self, value, expected_result, expected_type, expectations):
        with expectations:
            result = _check_value_is_bool(value)
            assert result == expected_result and isinstance(result, expected_type)

    @pytest.mark.parametrize(
        'value, expected_result, expected_type, expectations',
        [

            ('', True, bool, does_not_raise()),
            ('asd', True, bool, does_not_raise()),
            (None, False, bool, does_not_raise()),
            (2, False, bool, does_not_raise()),
            (2.0, False, bool, does_not_raise()),
            (True, False, bool, does_not_raise()),

        ]
    )
    def test_check_value_is_string(self, value, expected_result, expected_type, expectations):
        with expectations:
            result = _check_value_is_string(value)
            assert result == expected_result and isinstance(result, expected_type)
