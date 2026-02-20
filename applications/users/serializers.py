from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'full_name',
            'ocupation',
            'genero',
            'date_birth',
            'avatar',
            'password1',
            'password2',
        )

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        return User.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            **validated_data
        )


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_final = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name',
            'ocupation',
            'genero',
            'date_birth',
            'avatar',
            'avatar_url',
            'avatar_final',
        )
        read_only_fields = ('email', 'ocupation')

    def get_avatar_final(self, obj):
        # Retorna avatar local si existe, sino el de Google
        if obj.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return obj.avatar_url or None


class UserPublicSerializer(serializers.ModelSerializer):
    """Para mostrar info pública de un usuario a otros."""
    avatar_final = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'avatar_final')

    def get_avatar_final(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return obj.avatar_url or None