from . import composer
from .arguments_matcher import ANY_ARG, ANY_ARGS
from .composer import expectation_suite

allow = composer.ExpectationSuite(False).allow
