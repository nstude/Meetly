from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Like, Post, Message
from source.api.serializers.user_serializers import UserReadSerializer

class LikeReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'content_object', 'timestamp']
        read_only_fields = fields

    def get_content_object(self, obj):
        return str(obj.content_object)


class LikeCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id']
        extra_kwargs = {
            'content_type': {'error_messages': {'unique': 'Вы уже поставили лайк этому объекту'}},
        }


    def validate(self, data):
        content_type = data['content_type']
        object_id = data['object_id']
        
        try:
            content_type.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'error': 'Объект не существует'
            })
            
        return data


class LikeDeleteSerializer(serializers.Serializer): 
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            Like.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Лайк не найден")

        return data

    def delete(self):
        like = Like.objects.get(id=self.validated_data['id'])
        like.delete()
        return