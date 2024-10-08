from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Submissions
from .serializers import SubmissionSerializers , UserSerializers
from .utils import create_code_file, execute_file
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
import multiprocessing as mp



def hello_world(request):
    return HttpResponse("Welcome to online ide")


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format =None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def register(request):
    serializer = UserSerializers(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializers(user).data,status=201)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializers
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):   #list method is get all
        # print(request.user) we can recognize who is sending the request
        # return super().list(request,args,kwargs) it is returning all the users
        return Response(UserSerializers(request.user).data,status=200)


class SubmissionsViewSet(ModelViewSet):
    queryset = Submissions.objects.all()
    serializer_class = SubmissionSerializers
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(user=request.user)
        return Response(self.get_serializer(queryset,many=True).data,status=200)

    #overwriting the get , post ,put methods
    def create(self, request, *args, **kwargs):
        request.data["status"] = "P"
        request.data["user"] = request.user.pk
        file_name = create_code_file(request.data.get("code"),request.data.get("language"))
        # below we are executing the file before saving it.It may cause blockage as may be the file
        # take way more time to execute while others request are still pending
        # what we can do is we called a child proccess and hence won't block the API
        # output = execute_file(file_name,request.data.get("language"))
        # request.data["output"] = output
        # return super().create(request,args,kwargs)
        serializer = SubmissionSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()


        p = mp.Process(target=execute_file, args=(file_name, request.data.get("language"),submission.pk))
        p.start()

        return Response({
            "message": "Submitted successfully"
        },status=200)


