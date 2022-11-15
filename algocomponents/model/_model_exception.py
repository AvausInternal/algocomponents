class MLModelException(Exception):
    """ Exception type for use within MLModel derived classes """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)