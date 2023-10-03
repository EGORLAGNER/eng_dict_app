import pytest

from core.services.excel_import.main import *

from contextlib import nullcontext as does_not_raise

from core.services.excel_import.main import _check_is_bool


class TestMain:
    @pytest.mark.parametrize(
        'value, res, expected_type, expectations',
        [

            ('', True, bool, does_not_raise()),

        ]
    )
    def test_check_for_bool_value(self, value, res, expected_type, expectations):
        with expectations:
            assert _check_is_bool(value) == res
