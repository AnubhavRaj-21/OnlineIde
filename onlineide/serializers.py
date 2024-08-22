from rest_framework import serializers
from .models import User, Submissions

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SubmissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Submissions
        fields = "__all__"