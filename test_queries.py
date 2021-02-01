import pytest

from queries import validate_date


def test_validate_date():
    from_date = '2019-08-01'
    
    expected_from = '2019-08-01'
    expected_to = '2019-08-02'
    
    actual_from, actual_to = validate_date(from_date)

    assert actual_from == expected_from
    assert actual_to == expected_to


def test_validate_date_not_date():
    from_date = 'not a date'
    
    with pytest.raises(Exception):
        actual_from, actual_to = validate_date(from_date)
