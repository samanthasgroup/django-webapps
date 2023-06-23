from django.db.models import Model
from rest_framework import serializers


class ValidationErrorSerializer(serializers.Serializer[Model]):
    """
    Used only in OpenAPI schema, unless we are going to redefine DRF default errors serializer.
    """

    # This means that we can have multiple errors for any field of serializer.
    field1 = serializers.ListField(child=serializers.CharField())
    field2 = serializers.ListField(child=serializers.CharField())
    non_field_errors = serializers.ListField(child=serializers.CharField())


class BaseAPIExceptionSerializer(serializers.Serializer[Model]):
    """
    Used only in OpenAPI schema, represents the response body for default Django API exception.
    """

    detail = serializers.CharField()
