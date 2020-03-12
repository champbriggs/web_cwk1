from django.shortcuts import render
from .models import Professor, Module, ProfessorModuleRating, ModuleInstance
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests
from decimal import *
import json

http_bad_response = HttpResponseBadRequest()
http_bad_response.status_code = 503
http_bad_response.reason_phrase = 'Unavailable Service'
http_bad_response['Content-Type'] = 'text/plain'

# Create your views here.
@csrf_exempt
def HandleRegisterRequest(request):
    if request.user.is_authenticated:
        http_bad_response.content = "You are already logged in!"
        return http_bad_response
    else:
        if request.method != 'POST':
            http_bad_response.content = "Only POST requests are allowed for this resource"
            return http_bad_response

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            user = User.objects.create_user(username, email, password)
            user.save()
            http_response = HttpResponse
            http_response.status_code = 201
            http_response.reason_phrase = 'CREATED'
            return http_response('Registration successful')

def HandleLoginRequest(request):
    if request.user.is_authenticated:
        http_bad_response.content = "You are already logged in!"
        return http_bad_response
    else:
        if request.method != 'GET':
            http_bad_response.content = "Only GET requests are allowed for this resource"
            return http_bad_response

        if request.method == 'GET':
            username = request.GET.get('username')
            password = request.GET.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if request.user.is_authenticated:
                    http_response = HttpResponse
                    http_response.status_code = 200
                    http_response.reason_phrase = 'OK'
                    return http_response("Login Successful")
            else:
                http_bad_response.content = "Invalid Username and Password"
                return http_bad_response

def HandleListRequest(request):
    if request.user.is_authenticated:
        if request.method != 'GET':
            http_bad_response.content = "Only GET requests are allowed for this resource"
            return http_bad_response

        if request.method == 'GET':
            data_list = []
            professor_list = []
            professorcode_list = []
            instance_list = ModuleInstance.objects.all()

            for i in instance_list:
                for p in i.professor.all():
                    professor_list.append(p.name)
                    professorcode_list.append(p.code)
                data = {'modcode': i.module.code, 'modname': i.module.name, 'year': i.year, 'semester': i.semester, 'professor': professor_list, 'professorcode': professorcode_list}
                data_list.append(data)
                professor_list = []
                professorcode_list = []

            http_response = HttpResponse (json.dumps(data_list))
            http_response['Content-Type'] = 'application/json'
            http_response.status_code = 200
            http_response.reason_phrase = 'OK'
            return http_response
    else:
        http_bad_response.content = "Please login before using any commands"
        return http_bad_response

def HandleViewRequest(request):
    if request.user.is_authenticated:
        view_found = False

        if request.method != 'GET':
            http_bad_response.content = "Only GET requests are allowed for this resource"
            return http_bad_response

        if request.method == 'GET':
            data_list = []
            professor_list = Professor.objects.all()

            for i in professor_list:
                star = ""
                try:
                    rating = i.total_rating / i.totalnum_rating
                except ZeroDivisionError as err:
                    return HttpResponse('Currently there is no professor rating')
                rating = Decimal(rating).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
                for j in range(int(rating)):
                    star += "*"
                data = {'professor': i.name, 'professorcode': i.code, 'rating': star}
                data_list.append(data)
                view_found = True

            if view_found == True:
                http_response = HttpResponse (json.dumps(data_list))
                http_response['Content-Type'] = 'application/json'
                http_response.status_code = 200
                http_response.reason_phrase = 'OK'
                return http_response
            else:
                http_bad_response.content = "Currently there is no professor rating"
                return http_bad_response
    else:
        http_bad_response.content = "Please login before using any commands"
        return http_bad_response

def HandleAverageRequest(request):
    if request.user.is_authenticated:
        if request.method != 'GET':
            http_bad_response.content = "Only GET requests are allowed for this resource"
            return http_bad_response

        if request.method == 'GET':
            professorcode = request.GET.get('professorcode')
            modcode = request.GET.get('modcode')
            data_list = []
            rating_found = False
            modulerating_list = ProfessorModuleRating.objects.all().values('professor', 'module', 'total_rating', 'totalnum_rating')

            for i in modulerating_list:
                m = Module.objects.get(id = i['module'])
                p = Professor.objects.get(id = i['professor'])
                if m.code == modcode and p.code == professorcode:
                    star = ""
                    rating = i['total_rating'] / i['totalnum_rating']
                    rating = Decimal(rating).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
                    for i in range(int(rating)):
                        star += "*"
                    data = {'modcode': m.code, 'modname': m.name, 'professorcode': p.code, 'professorname': p.name, 'rating': star}
                    data_list.append(data)
                    rating_found = True

            if rating_found == True:
                http_response = HttpResponse (json.dumps(data_list))
                http_response['Content-Type'] = 'application/json'
                http_response.status_code = 200
                http_response.reason_phrase = 'OK'
                return http_response
            else:
                return http_bad_response("There is no such rating with professor_id: " + professorcode + ", module_code: " + modcode)
    else:
        http_bad_response.content = "Please login before using any commands"
        return http_bad_response

@csrf_exempt
def HandleRateRequest(request):
    if request.user.is_authenticated:
        if request.method != 'POST':
            http_bad_response.content = "Only POST requests are allowed for this resource"
            return http_bad_response

        if request.method == 'POST':
            professorcode = request.POST.get('professorcode')
            modcode = request.POST.get('modcode')
            year = request.POST.get('year')
            semester = request.POST.get('semester')
            rating = request.POST.get('rating')
            instance_found = False
            rating_found = False

            instance_list = ModuleInstance.objects.all().values('module', 'professor', 'year', 'semester')
            for i in instance_list:
                m = Module.objects.get(id = i['module'])
                p = Professor.objects.get(id = i['professor'])

                if m.code == modcode and p.code == professorcode and i['year'] == year and i['semester'] == semester:
                    instance_found = True
                    modulerating_list = ProfessorModuleRating.objects.all().values('professor', 'module', 'total_rating', 'totalnum_rating')

                    if len(modulerating_list) == 0:
                        new_modulerating = ProfessorModuleRating(professor = p, module = m, total_rating = rating, totalnum_rating = 1)
                        p.total_rating += int(rating)
                        p.totalnum_rating += 1
                        p.save()
                        new_modulerating.save()
                    else:
                        for j in modulerating_list:
                            m2 = Module.objects.get(id = j['module'])
                            p2 = Professor.objects.get(id = j['professor'])
                            if m2.code == modcode and p2.code == professorcode:
                                edit_rating = ProfessorModuleRating.objects.get(professor = p2, module = m2)
                                edit_rating.total_rating += int(rating)
                                edit_rating.totalnum_rating += 1
                                p2.total_rating += int(rating)
                                p2.totalnum_rating += 1
                                p2.save()
                                edit_rating.save()
                                rating_found = True

                        if rating_found == False:
                            new_modulerating = ProfessorModuleRating(professor = p, module = m, total_rating = rating, totalnum_rating = 1)
                            p.total_rating += int(rating)
                            p.totalnum_rating += 1
                            p.save()
                            new_modulerating.save()

            if instance_found == True:
                http_response = HttpResponse
                http_response.status_code = 200
                http_response.reason_phrase = 'OK'
                return http_response('Rating submitted successfully')
            else:
                return http_bad_response("There is no such module instance with professor_id: " + professorcode + ", module_code: " + modcode + ", year: " + year + ", semester: " + semester)
    else:
        http_bad_response.content = "Please login before using any commands"
        return http_bad_response


def HandleLogoutRequest(request):
    if request.user.is_authenticated:
        logout(request)
        http_response = HttpResponse
        http_response.status_code = 200
        http_response.reason_phrase = 'OK'
        return http_response("Logout Successful")
    else:
        http_bad_response.content = "Please login before using any commands"
        return http_bad_response
