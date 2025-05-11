from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Like, Post, Message
from source.api.serializers.user_serializers import UserReadSerializer

class LikeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'content_type', 'object_id', 'timestamp']
        extra_kwargs = {
            'id': {'read_only': True},
            'timestamp': {'read_only': True},
            'content_type': {
                'error_messages': {
                    'unique': 'Вы уже поставили лайк этому объекту'
                }
            }
        }

    def validate(self, data):
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        
        if content_type and object_id:
            try:
                content_type.get_object_for_this_type(pk=object_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError({
                    'error': 'Объект не существует'
                })
            
        return data


class LikeReadSerializer(LikeBaseSerializer):
    user = UserReadSerializer(read_only=True)
    content_object = serializers.SerializerMethodField()

    class Meta(LikeBaseSerializer.Meta):
        fields = LikeBaseSerializer.Meta.fields + ['user', 'content_object']
        read_only_fields = fields

    def get_content_object(self, obj):
        return str(obj.content_object)


class LikeCreateSerializer(LikeBaseSerializer):
    """
    # TO DO Аналогично посту
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta(LikeBaseSerializer.Meta):
        fields = LikeBaseSerializer.Meta.fields + ['user']


class LikeDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        if not Like.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Лайк не найден")
        return data

    def delete(self):
        Like.objects.filter(id=self.validated_data['id']).delete()