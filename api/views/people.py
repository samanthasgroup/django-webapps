from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.people import Student  # , Teacher
from api.serializers.people import StudentSerializer  # , TeacherSerializer


class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDetail(APIView):
    def get_object(self, uuid):
        try:
            return Student.objects.get(personal_info_id=uuid)
        except Student.DoesNotExist:
            raise Http404

    def get(self, uuid):
        student = self.get_object(uuid)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, uuid):
        student = self.get_object(uuid)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
class TeacherList(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class TeacherDetails(generics.RetrieveAPIView()):   
    pass

"""
