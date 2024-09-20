from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        
class MessegesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messeges
        fields = '__all__'
        

