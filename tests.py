from validatorchain import ValidatorChain
from django.forms import CharField
from django.core.exceptions import ValidationError
import pytest


def test_skip_on_error():
    """
    If a previous validator errored out one marked as `skip_on_error` should
    not be executed.
    """
    executed = [False, False, False]

    def val1(value):
        executed[0] = True
        raise Exception("An error occurred")

    def val2(value):
        executed[1] = True

    def val3(value):
        executed[2] = True

    chain = ValidatorChain().add(val1).add(val2, skip_on_error=True).add(val3)
    errors = []
    for validator in chain:
        try:
            validator(True)
        except Exception as e:
            errors.append(e)

    assert executed == [True, False, True]


def test_execute_all_if_no_error():
    """
    If no error occurs, every validator should be executed.
    """
    executed = [False, False, False]

    def val1(value):
        executed[0] = True

    def val2(value):
        executed[1] = True

    def val3(value):
        executed[2] = True

    chain = ValidatorChain().add(val1).add(val2, skip_on_error=True).add(val3)
    errors = []
    for validator in chain:
        try:
            validator(True)
        except Exception as e:
            errors.append(e)

    assert executed == [True, True, True]


def test_reverse_addition():
    """
    Each form field comes with a default list of validators to which the
    custom ones are added. The end result of such an addition has to be
    a ValidatorChain with the default validators not being marked as skippable.
    """
    def val(val):
        pass
    result = [val, val] + ValidatorChain().add(val, skip_on_error=True)
    assert isinstance(result, ValidatorChain)
    assert len(result) == 3
    assert not result._data[0].skip_on_error
    assert not result._data[1].skip_on_error
    assert result._data[2].skip_on_error


def test_addition():
    """
    In case you add a list of validators to another one, make sure that the
    result is still a validator chain and that skip-states are preserved.
    """
    def val(val):
        pass
    result = ValidatorChain().add(val, skip_on_error=True) + [val]
    assert isinstance(result, ValidatorChain)
    assert len(result) == 2
    assert result._data[0].skip_on_error
    assert not result._data[1].skip_on_error


def test_form_validation():
    text = CharField(validators=[])
    text.clean('invalid')

    def require_value(val):
        if val == 'invalid':
            raise ValidationError("Invalid value!")

    text = CharField(validators=ValidatorChain().add(require_value))
    with pytest.raises(ValidationError):
        text.clean('invalid')

def test_form_validation_empty_value():
    """
    If you allow empty values then no validators are executed by Django itself
    hence in this case no exception will be raised by the require_value
    validator.

    This is due to https://github.com/django/django/blob/master/django/forms/fields.py#L131
    """
    text = CharField(validators=[], required=False)
    text.clean('')

    def require_value(val):
        raise ValidationError("Invalid value!")

    text = CharField(validators=ValidatorChain().add(require_value), required=False)
    text.clean('')
