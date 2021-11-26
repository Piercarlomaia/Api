from rest_framework import serializers
from Api.models import User, Chaves


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class ChavesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chaves
        fields = '__all__'