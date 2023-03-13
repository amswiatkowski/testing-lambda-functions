from functools import wraps


def mock_ssm_parameter_store_decorator(*parameters):
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            if not hasattr(context, "parameters"):
                context.parameters = {}
            context.parameters['DummySSM'] = 'My Fake SSM Value'
            return handler(event, context)

        return wrapper

    return wrapper_wrapper
