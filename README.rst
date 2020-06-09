django-validatorchain
#####################

.. warning::

    This project is no longer maintained as Django in 2017 introduced a change
    that no longer allows the workaround implemented here. Please see `this
    issue`_ for details.


Motivation
==========

While working on the EuroPython 2014 website we ran into a situation where we
had a field validator that was rather expensive to evaluate.

Sadly, the `validators-attribute`_ on a model/form field is always evaluated as
a whole (meaning each validator in that list is executed no matter if a previous
one errored out already). So, we wanted to have a way to mark certain validators
as not to be executed in case the field was being marked as invalid anyway.

We still wanted to use the field validator API simply because it keeps
everything easily testible, though.


How to use
==========

::

    from django.db import models

    from validatorchain import ValidatorChain

    from .validators import a_cheap_validator
    from .validators import another_cheap_validator
    from .validators import an_expensive_validator


    class SomeModel(models.Model):
        field = models.CharField(
            max_length=100,
            validators=ValidatorChain()
                .add(a_cheap_validator)
                .add(an_expensive_validator, skip_on_error=True)
                .add(another_cheap_validator)
            )

This way `an_expensive_validator` will not be executed if `a_cheap_validator`
already raised an exception, while `another_cheap_validator` will be executed
again.

.. _this issue: https://github.com/zerok/django-validatorchain/issues/1
.. _validators-attribute: https://docs.djangoproject.com/en/1.5/ref/forms/validation/#validators
