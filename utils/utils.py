from collections import namedtuple


Status = namedtuple('Status', field_names=[
    'HTTP_200_OK', 'HTTP_400_BAD_REQUEST', 'HTTP_404_NOT_FOUND',
])
status = Status(200, 400, 404)
