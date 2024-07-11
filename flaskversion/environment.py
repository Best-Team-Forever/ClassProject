from behave import *


def after_scenario(context, scenario):
    if hasattr(context, 'database'):
        context.database.close()
