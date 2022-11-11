class AdapterException(Exception):
    pass


class TableMissingException(AdapterException):
    pass


class TableAlreadyExistsException(AdapterException):
    pass


class DatabaseMissingException(AdapterException):
    pass


class ColumnMissingException(AdapterException):
    pass


class DataMismatchException(AdapterException):
    pass
