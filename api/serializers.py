from rest_framework.serializers import Serializer


class ReadOnlySerializer(Serializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
