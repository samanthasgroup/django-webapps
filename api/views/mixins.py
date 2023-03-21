from rest_framework import request, serializers
from rest_framework.permissions import SAFE_METHODS


class ReadWriteSerializersMixin:
    """
    Mixin for ViewSet for defining different serializers for read and write.
    """

    # Typings for attributes which are set in ViewSet
    request: request.Request
    serializer_class: type[serializers.BaseSerializer] | None
    serializer_read_class: type[serializers.BaseSerializer]
    serializer_write_class: type[serializers.BaseSerializer]

    def get_serializer_class(self) -> type[serializers.BaseSerializer]:
        """
        Return the class to use for the serializer.
        """
        if self.request.method in SAFE_METHODS:
            return self.serializer_read_class

        return self.serializer_write_class
