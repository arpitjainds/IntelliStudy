from __future__ import print_function
import random
import numpy as np
import datetime
import pytz
from dateutil import parser
import scipy.stats
import scipy.spatial
from sklearn.cross_validation import KFold
import random
from sklearn.metrics import mean_squared_error
from math import sqrt
import math
import warnings
import sys


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from .models import (Course, Enroll, Student, Mentor, Question, ExtraInfo, Content, Manage, Score,
                     File, Option, Contain, Group, Career, Has)
from .forms import AddSubtopic
import numpy as np
import xlrd
import os

def auth(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username = username, password = password)
    extrainfo = ExtraInfo.objects.get(user=user)
    if extrainfo.user_type == "student":
        student = Student.objects.get(unique_id=extrainfo)
        score = Score.objects.filter(unique_id=student)
        counter = 0
        flag = 0
        for s in score:
            if s.marks != -1:
                counter = counter + 10
                flag = flag + s.marks
        if counter > 0:
            avg = (flag * 100)/counter
            if avg > 80:
                student.level = "advanced"
            elif avg > 60:
                student.level = "intermediate"
            else:
                stduent.level = "beginner"
    if user is not None:
        login(request, user)
        if extrainfo.user_type == "student":
            return redirect('/epsilon/dashboard')
        else:
            return redirect('/epsilon/mdashboard')
    else:
        return redirect('/epsilon')

def signup(request):
    if 'student' in request.POST:
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(password)
        user, created = User.objects.get_or_create(username = username)
        if created:
            user.set_password(password)
            user.first_name = fname
            user.last_name = lname
            user.email = email
            user.save()
        gender = request.POST.get("gender")
        job = request.POST.get("job")
        qualification = request.POST.get("qualification")
        dob = request.POST.get("dob")
        info = ExtraInfo(user=user , sex=gender, date_of_birth=dob, user_type="student", job=job, qualification=qualification)
        info.save()
        stud = Student(unique_id=info, level="beginner")
        stud.save()
        login(request, user)
        return redirect('/epsilon/dashboard')
    else:
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(password)
        user, created = User.objects.get_or_create(username = username)
        if created:
            user.set_password(password)
            user.first_name = fname
            user.last_name = lname
            user.email = email
            user.save()
        gender = request.POST.get("gender")
        job = request.POST.get("job")
        qualification = request.POST.get("qualification")
        dob = request.POST.get("dob")
        info = ExtraInfo(user=user , sex=gender, date_of_birth=dob, user_type="mentor", job=job, qualification=qualification)
        info.save()
        mentor = Mentor(mentor_id=info)
        mentor.save()
        login(request, user)
        return redirect('/epsilon/mdashboard')

    # return HttpResponse("successfully signed up")

def index(request):
    context = {}
    return render(request, "epsilon/index.html", context)


def student(request):
    context = {}
    return render(request, "epsilon/loginstudent.html", context)


def mentor(request):
    context = {}
    return render(request, "epsilon/mentorlogin.html", context)


@login_required
def dashboard(request):
    user = request.user
    s= Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))
    courses = Course.objects.all()
    career = Career.objects.all()
    if Enroll.objects.filter(unique_id = s):
        r = RBM()
        q = r.RBMx(s)
    else:
        q=[]
    context = {'courses': courses, 'career': career, 'recommended':q}
    return render(request, "epsilon/student_dashboard.html", context)


@login_required
def course(request):
    user = request.user
    if 'course' in request.POST:
        cid = request.POST.get('course')
        course = Course.objects.get(Q(pk=cid))
        enroll = Enroll.objects.filter(Q(unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)),
                                         course_id=course))
    if 'join' in request.POST:
        cid = request.POST.get('join')
        course = Course.objects.get(Q(pk=cid))
        enroll = Enroll.objects.create(course_id=course, unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)))
        content = Content.objects.filter(Q(course_id=course))
        for c in content:
            score = Score.objects.create(content_id = c, unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)))
        enroll.save()
    if 'leave' in request.POST:
        cid = request.POST.get('leave')
        course = Course.objects.get(Q(pk=cid))
        enroll = Enroll.objects.filter(Q(unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)),
                                         course_id=course))
        content = Content.objects.filter(Q(course_id=course))
        contain = Contain.objects.filter(Q(group_id=Group.objects.filter(Q(course_id=course)),
                                           unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))))
        if contain.exists():
            contain.delete()
        for c in content:
            score = Score.objects.filter(Q(content_id = c, unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))))
            score.delete()
        enroll.delete()
    if 'feedback' in request.POST:
        cid = request.POST.get('feedback')
        course = Course.objects.get(Q(pk=cid))
        enroll = Enroll.objects.get(unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)),
                                         course_id=course)
        enroll.feedback = request.POST.get('text')
        enroll.save()
    content = Content.objects.filter(Q(course_id=course))
    score = Score.objects.filter(Q(unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)),
                                   content_id__in=content))
    flag=0
    counter=0
    for s in score:
        counter=counter+1
        if s.progress == "COMPLETED":
            flag=flag+1
    if counter != 0:
        progress = (flag * 100)/counter
    else:
        progress = 0
    mentor = Mentor.objects.filter(Q(pk__in=Manage.objects.filter(Q(course_id=course)).values('mentor_id_id')))
    group = Group.objects.filter(Q(course_id=course))
    if group:
        contain = Contain.objects.filter(Q(group_id=Group.objects.get(course_id=course),
                                           unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))))
    else:
        contain = []
    context = {'course': course, 'content': content, 'mentor': mentor, 'enroll': enroll, 'score': score, 'progress': progress, 'contain': contain}
    return render(request, "epsilon/coursemain.html", context)


@login_required
def career(request):
    user = request.user
    if 'career' in request.POST:
        career_id = request.POST.get('career')
        career = Career.objects.get(Q(pk=career_id))
        has = sorted(Has.objects.filter(Q(career_id=career)), key=lambda t: t.order)
        print(has)
    context = {'career': career, 'has': has}
    return render(request, "epsilon/careerpath.html", context)


@login_required
def quiz(request):
    if 'givequiz' in request.POST:
        cid = request.POST.get('givequiz')
        content = Content.objects.get(pk=cid)
        user=request.user
        unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))
        quiz = Question.objects.filter(Q(content_id=content, level=unique_id.level))
        questions = random.sample(list(quiz), 10)
        option = Option.objects.filter(Q(question_id__in=questions))
        context = {'content': content, 'questions': questions, 'option': option}
        return render(request, "epsilon/quiz.html", context)
    if 'give' in request.POST:
        cid = request.POST['give']
        content = Content.objects.get(pk=cid)
        score = 0
        questions = []
        a = [0 for x in range(1,11)]
        for q in range(1,10):
            qp = request.POST.get(str(q))
            que = Question.objects.get(pk=qp)
            o = request.POST.get(que.question)
            questions.append(que)
            if o:
                if o == que.answer:
                    a[q] = "correct"
                    score = score + 1
                else:
                    a[q] = "incorrect"
            else:
                a[q] = "not attempted"
        option = Option.objects.filter(Q(question_id__in=questions))
        context = {'content': content, 'option': option, 'a': a, 'questions': questions, 'score': score}
        return render(request, "epsilon/quiz.html", context)


@login_required
def mycourses(request):
    user = request.user
    course = Course.objects.filter(Q(pk__in=Enroll.objects.filter(Q(unique_id__in=Student.objects.filter(Q(unique_id__in=ExtraInfo.objects.filter(Q(user=user)))))).values('course_id_id')))
    context = {'courses': course}
    return render(request, "epsilon/mycourses.html", context)


@login_required
def profile(request):
    user = request.user
    extrainfo = ExtraInfo.objects.get(user=user)
    context = {'extrainfo': extrainfo, 'user':user}
    return render(request, "epsilon/profile.html", context)

@login_required
def update_profile(request):
    user = request.user
    extrainfo = ExtraInfo.objects.get(user=user)
    job = request.POST.get("job_opt")
    qualification = request.POST.get("qualify_opt")

    password = request.POST.get("password")
    extrainfo.job = job
    extrainfo.qualification = qualification
    extrainfo.profile_picture = request.POST.get("profile_pic")
    extrainfo.save()

    if password is not "":
        user.set_password(password)
        user.save()

    context = {'extrainfo': extrainfo, 'user':user}

    profile(request)
    return render(request, "epsilon/profile.html", context)

@login_required
def study(request):
    cid = request.POST.get('content')
    content = Content.objects.get(pk=cid)
    file = File.objects.filter(Q(content_id=content))
    user=request.user
    unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))
    quiz = Question.objects.filter(Q(content_id=content, level=unique_id.level))
    context = {'content': content, 'file': file}
    return render(request, "epsilon/coursestudy.html", context)


@login_required
def group(request):
    user = request.user
    if 'group' in request.POST:
        cid = request.POST.get('group')
        course = Course.objects.get(pk=cid)
        contain = Contain.objects.get(group_id__in=Group.objects.filter(Q(course_id=course)),
                                      unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user)))
        students = Student.objects.filter(Q(unique_id__in=Contain.objects.filter(Q(group_id=Group.objects.filter(Q(course_id=course)))).values('unique_id_id')))
        context = {'course': course, 'students': students}
        return render(request, "epsilon/coursegroup.html", context)
    if 'join' in request.POST:
        cid = request.POST.get('join')
        course = Course.objects.get(pk=cid)
        flag = 0
        student = Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))
        group=Group.objects.filter(Q(course_id=course, level=student.level))
        for g in group:
            contain = Contain.objects.filter(Q(group_id=g))
            counter = 0
            for c in contain:
                counter = counter + 1
            if counter<5:
                contain = Contain.objects.create(group_id=g, unique_id=student)
                contain.save()
                flag = 1
                break
        if flag == 0:
            group = Group.objects.create(course_id=course, level=student.level)
            group.save()
            contain = Contain.objects.create(group_id=group, unique_id=student)
            contain.save()


def about(request):
    return render(request, 'epsilon/about.html')


@login_required
def mdashboard(request):
    courses = Course.objects.all()
    career = Career.objects.all()
    context = {'courses': courses, 'career': career}
    return render(request, "epsilon/mentor_dashboard.html", context)


@login_required
def manage(request):
    user = request.user
    m = ExtraInfo.objects.get(user = user)
    mentor = Mentor.objects.get(mentor_id = m)
    man = Manage.objects.filter(mentor_id = mentor)
    courses = []
    for i in man:
        c = Course.objects.get(id=i.course_id.id)
        courses.append(c)
    context = {'courses': courses}
    return render(request, "epsilon/managecourses.html", context)


@login_required
def edittopic(request):
    user = request.user
    m = ExtraInfo.objects.get(user = user)
    mentor = Mentor.objects.get(mentor_id = m)
    content = Content.objects.get(id = request.POST['content'])
    form = AddSubtopic()
    context = {'content': content,
                'form' : form}
    if request.method == 'POST' and request.FILES:
        fileForm = AddSubtopic(initial={'content_id':content,
                                        'mentor_id':mentor})
        fileForm = AddSubtopic(request.FILES, request.POST)
        if fileForm.is_valid():
            print("kkkkkk")
            fileForm.save()
    return render(request, "epsilon/editsubtopic.html", context)


@login_required
def editquiz(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, "epsilon/editquiz.html", context)


@login_required
def editcourse(request):
    course = Course.objects.get(id = request.POST['course'])
    contents = Content.objects.filter(course_id = request.POST['course'])
    context = {'contents': contents,
                'course': course}
    return render(request, "epsilon/editcourse.html", context)


@login_required
def loggedout(request):
    logout(request)
    return redirect('/epsilon')


@login_required
def reco(request):
    user = request.user
    high1, high2, low1, low2 = recommender_related(user)
    return redirect('/epsilon/reco')


@login_required
def apt(request):
    if 'join' in request.POST:
        cid = request.POST.get('join')
        request.session['count'] = 0
        request.session['score'] = 0
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        request.session['time'] = str(now)
        diff = []
        request.session['diff'] = diff
        course = Course.objects.get(pk=cid)
        user=request.user
        unique_id=Student.objects.get(unique_id=ExtraInfo.objects.get(user=user))
        quiz = Question.objects.filter(Q(content_id=Content.objects.filter(Q(course_id=course)), level="intermediate"))
        question = random.sample(list(quiz), 1)
        for q in question:
            print(q.avg_time)
            request.session['avg'] = q.avg_time
            option = Option.objects.filter(Q(question_id=q))
        context = {'course': course, 'question': question, 'option': option}
        return render(request, "epsilon/aptquiz.html", context)
    if 'next' in request.POST:
        x = request.session['count']
        if x < 9:
            cid = request.POST['next']
            request.session['count'] = request.session['count'] + 1
            print(request.session['count'])
            course = Course.objects.get(pk=cid)
            qp = request.POST.get('ques')
            que = Question.objects.get(pk=qp)
            o = request.POST.get(que.question)
            if o:
                if o == que.answer:
                    a = 1
                    request.session['score'] = request.session['score'] + 1
                else:
                    a = 0
            else:
                a = 0
            now = request.session['time']
            now = parser.parse(now)
            timediff = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - now
            x = timediff.total_seconds()
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            avg = request.session['avg']
            diff = request.session['diff']
            if a==0:
                diff.append(-1)
            else:
                v = (avg-x)/avg
                if v > 1.3:
                    v = 1.3
                elif v < -1.3:
                    v = -1.3
                diff.append(float(v))
            print(diff)
            output = quiz_reccomend1(diff, request.session['count'])
            request.session['diff'] = diff
            request.session['time'] = str(now)
            if output == 0:
                level="beginner"
            elif output == 1:
                level="intermediate"
            elif output == 2:
                level="advanced"
            else:
                print("ERRORR!!!")
            print(level)
            quiz = Question.objects.filter(Q(content_id=Content.objects.filter(Q(course_id=course)), level=level))
            question = random.sample(list(quiz), 1)
            for q in question:
                request.session['avg'] = q.avg_time
                option = Option.objects.filter(Q(question_id=q))
            context = {'course': course, 'question': question, 'option': option}
            return render(request, "epsilon/aptquiz.html", context)
        else:
            cid = request.POST['next']
            request.session['count'] = request.session['count'] + 1
            course = Course.objects.get(pk=cid)
            qp = request.POST.get('ques')
            que = Question.objects.get(pk=qp)
            o = request.POST.get(que.question)
            if o:
                if o == que.answer:
                    a = 1
                    request.session['score'] = request.session['score'] + 1
                else:
                    a = 0
            else:
                a = 0
            now = request.session['time']
            now = parser.parse(now)
            timediff = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - now
            x = timediff.total_seconds()
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            avg = request.session['avg']
            diff = request.session['diff']
            if a==0:
                diff.append(-1)
            else:
                v = (avg-x)/avg
                if v > 1.3:
                    v = 1.3
                elif v < -1.3:
                    v = -1.3
                diff.append(float(v))
            output = quiz_reccomend1(diff, request.session['count'])
            request.session['diff'] = diff
            if output == 0:
                level="beginner"
            elif output == 1:
                level="intermediate"
            elif output == 2:
                level="advanced"
            else:
                print("ERRORR!!!")
            score = request.session['score']
            context = {'course': course, 'score': score, 'level': level}
            return render(request, "epsilon/aptquiz.html", context)



# Sigmoid Function
def sigmoid (x):
    return 1/(1 + np.exp(-x))

#Derivative of Sigmoid Function
def derivatives_sigmoid(x):
    return x * (1 - x)


def quiz_reccomend1(x, t):
    # Input
    if (t == 1):
        X = np.array([[0.9], [1.2], [0.8], [0.2], [0.15], [-0.20], [-0.6], [-0.8], [-0.9]])
    elif (t == 2):
        X = np.array(
            [[0.9, 0.6], [1.2, 0.4], [0.8, 0.9], [0.2, -0.2], [0.15, 0.3], [-0.20, 0.4], [-0.6, -0.4], [-0.8, -0.3],
             [-0.9, -0.2]])
    elif (t == 3):
        X = np.array(
            [[0.9, 0.6, 0.7], [1.2, 0.4, 0.6], [0.8, 0.9, 0.6], [0.2, -0.2, 0.1], [0.15, 0.3, 0.1], [-0.20, 0.4, -0.1],
             [-0.6, -0.4, -0.3], [-0.8, -0.3, -0.4], [-0.9, -0.2, -0.3]])
    elif (t == 4):
        X = np.array([[0.9, 0.6, 0.7, 0.8], [1.2, 0.4, 0.6, 1.3], [0.8, 0.9, 0.6, 0.7], [0.2, -0.2, 0.1, -0.2],
                      [0.15, 0.3, 0.1, -0.2], [-0.20, 0.4, -0.1, 0.1], [-0.6, -0.4, -0.3, -0.4],
                      [-0.8, -0.3, -0.4, -0.5], [-0.9, -0.2, -0.3, -0.4]])
    elif (t == 5):
        X = np.array([[0.9, 0.6, 0.7, 0.8, 0.5], [1.2, 0.4, 0.6, 1.3, 0.5], [0.8, 0.9, 0.6, 0.7, 0.9],
                      [0.2, -0.2, 0.1, -0.2, 0.1],
                      [0.15, 0.3, 0.1, -0.2, -0.1], [-0.20, 0.4, -0.1, 0.1, -0.2], [-0.6, -0.4, -0.3, -0.4, -0.4],
                      [-0.8, -0.3, -0.4, -0.5, -1.0], [-0.9, -0.2, -0.3, -0.4, -0.7]])
    elif (t == 6):
        X = np.array([[0.9, 0.6, 0.7, 0.8, 0.5, 0.7], [1.2, 0.4, 0.6, 1.3, 0.5, 0.8], [0.8, 0.9, 0.6, 0.7, 0.9, 0.7],
                      [0.2, -0.2, 0.1, -0.2, 0.1, 0.3],
                      [0.15, 0.3, 0.1, -0.2, -0.1, 0.2], [-0.20, 0.4, -0.1, 0.1, -0.2, 0.3],
                      [-0.6, -0.4, -0.3, -0.4, -0.4, -0.3],
                      [-0.8, -0.3, -0.4, -0.5, -1.0, 0.2], [-0.9, -0.2, -0.3, -0.4, -0.7, 0.1]])
    elif (t == 7):
        X = np.array([[0.9, 0.6, 0.7, 0.8, 0.5, 0.7, 0.9], [1.2, 0.4, 0.6, 1.3, 0.5, 0.8, 0.6],
                      [0.8, 0.9, 0.6, 0.7, 0.9, 0.7, 1.2],
                      [0.2, -0.2, 0.1, -0.2, 0.1, 0.3, 0.2], [0.15, 0.3, 0.1, -0.2, -0.1, 0.2, 0.2],
                      [-0.20, 0.4, -0.1, 0.1, -0.2, 0.3, -0.1],
                      [-0.6, -0.4, -0.3, -0.4, -0.4, -0.3, -0.8], [-0.8, -0.3, -0.4, -0.5, -1.0, 0.2, -0.8],
                      [-0.9, -0.2, -0.3, -0.4, -0.7, -0.3, -0.8]])
    elif (t == 8):
        X = np.array([[0.9, 0.6, 0.7, 0.8, 0.5, 0.7, 0.9, 0.6], [1.2, 0.4, 0.6, 1.3, 0.5, 0.8, 0.6, 0.9],
                      [0.8, 0.9, 0.6, 0.7, 0.9, 0.7, 1.2, 0.9],
                      [0.2, -0.2, 0.1, -0.2, 0.1, 0.3, 0.2, -0.1], [0.15, 0.3, 0.1, -0.2, -0.1, 0.2, 0.2, -0.2],
                      [-0.20, 0.4, -0.1, 0.1, -0.2, 0.3, -0.1, 0.2],
                      [-0.6, -0.4, -0.3, -0.4, -0.4, -0.3, -0.8, 0.2], [-0.8, -0.3, -0.4, -0.5, -1.0, 0.2, -0.8, -0.5],
                      [-0.9, -0.2, -0.3, -0.4, -0.7, -0.3, -0.8, -0.4]])
    elif (t == 9):
        X = np.array([[0.9, 0.6, 0.7, 0.8, 0.5, 0.7, 0.9, 0.6, 0.9], [1.2, 0.4, 0.6, 1.3, 0.5, 0.8, 0.6, 0.9, 0.8],
                      [0.8, 0.9, 0.6, 0.7, 0.9, 0.7, 1.2, 0.9, 1.0],
                      [0.2, -0.2, 0.1, -0.2, 0.1, 0.3, 0.2, -0.1, 0.3],
                      [0.15, 0.3, 0.1, -0.2, -0.1, 0.2, 0.2, -0.2, -0.2],
                      [-0.20, 0.4, -0.1, 0.1, -0.2, 0.3, -0.1, 0.2, -0.2],
                      [-0.6, -0.4, -0.3, -0.4, -0.4, -0.3, -0.8, 0.2, -0.6],
                      [-0.8, -0.3, -0.4, -0.5, -1.0, 0.2, -0.8, -0.5, -0.7],
                      [-0.9, -0.2, -0.3, -0.4, -0.7, -0.3, -0.8, -0.4, 0.4]])
    elif (t == 10):
        X = np.array(
            [[0.9, 0.6, 0.7, 0.8, 0.5, 0.7, 0.9, 0.6, 0.9, -0.4], [1.2, 0.4, 0.6, 1.3, 0.5, 0.8, 0.6, 0.9, 0.8, 0.6],
             [0.8, 0.9, 0.6, 0.7, 0.9, 0.7, 1.2, 0.9, 1.0, -0.6],
             [0.2, -0.2, 0.1, -0.2, 0.1, 0.3, 0.2, -0.1, 0.3, -.4],
             [0.15, 0.3, 0.1, -0.2, -0.1, 0.2, 0.2, -0.2, -0.2, 0.3],
             [-0.20, 0.4, -0.1, 0.1, -0.2, 0.3, -0.1, 0.2, -0.2, 0],
             [-0.6, -0.4, -0.3, -0.4, -0.4, -0.3, -0.8, 0.2, -0.6, 0.4],
             [-0.8, -0.3, -0.4, -0.5, -1.0, 0.2, -0.8, -0.5, -0.7, -0.4],
             [-0.9, -0.2, -0.3, -0.4, -0.7, -0.3, -0.8, -0.4, 0.4, -0.8]])
    # Output
    y = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1], [0, 0, 1]])

    # Variable initialization
    epoch = 5000  # Setting training iterations
    lr = 0.1  # Setting learning rate
    inputlayer_neurons = X.shape[1]  # number of features in data set
    hiddenlayer_neurons = 10  # number of hidden layers neurons
    output_neurons = 3  # number of neurons at output layer
    # weight and bias initialization
    wh1 = np.random.uniform(size=(inputlayer_neurons, hiddenlayer_neurons))
    bh1 = np.random.uniform(size=(1, hiddenlayer_neurons))
    wout1 = np.random.uniform(size=(hiddenlayer_neurons, output_neurons))
    bout1 = np.random.uniform(size=(1, output_neurons))
    for i in range(epoch):
        # Forward Propogation
        hidden_layer_input1 = np.dot(X, wh1)
        hidden_layer_input = hidden_layer_input1 + bh1
        hiddenlayer_activations = sigmoid(hidden_layer_input)
        output_layer_input1 = np.dot(hiddenlayer_activations, wout1)
        output_layer_input = output_layer_input1 + bout1
        output = sigmoid(output_layer_input)

        # Backpropagation
        E = y - output
        slope_output_layer = derivatives_sigmoid(output)
        slope_hidden_layer = derivatives_sigmoid(hiddenlayer_activations)
        d_output = E * slope_output_layer
        Error_at_hidden_layer = d_output.dot(wout1.T)
        d_hiddenlayer = Error_at_hidden_layer * slope_hidden_layer
        wout1 += hiddenlayer_activations.T.dot(d_output) * lr
        bout1 += np.sum(d_output, axis=0, keepdims=True) * lr
        wh1 += X.T.dot(d_hiddenlayer) * lr
        bh1 += np.sum(d_hiddenlayer, axis=0, keepdims=True) * lr

    hidden_layer_input1 = np.dot(x, wh1)
    hidden_layer_input = hidden_layer_input1 + bh1
    hiddenlayer_activations = sigmoid(hidden_layer_input)
    output_layer_input1 = np.dot(hiddenlayer_activations, wout1)
    output_layer_input = output_layer_input1 + bout1
    output = sigmoid(output_layer_input)
    print(output)
    if ((output[0][0] > output[0][1]) and (output[0][0] > output[0][2])):
        return 2
    elif (output[0][1] > output[0][2]):
        return 1
    else:
        return 0


class RBM:

    def __init__(self):
        skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data1.xlsx'))

    def RBMx(self,s):
        skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data1.xlsx'))
        z = skillexcel.sheet_by_index(0)
        arr = []
        for i in range(1, 16):
            row = []
            try:
                for j in range(0,19):
                    row.append(int(z.cell(i,j+1).value))

            except Exception as e:
                print(e)
                print(i)
            arr.append(row)

        self.RBMstart(num_visible = 19, num_hidden = 16)
        training_data = np.array(arr)
        self.train(training_data, max_epochs = 5000)
        e = Enroll.objects.filter(unique_id = s)
        course = Course.objects.all()
        career = Career.objects.all()
        a = []
        for c in course:
            if Enroll.objects.filter(course_id = c):
                a.append(1)
            else:
                a.append(0)

        q = []
        print(a)
        user = np.array([a])
        t = self.run_visible(user)
        print(t)
        for x in t:
            for i in range(len(x)):
                if x[i]!=0.0:
                    q.append(career[i])
        return q

    def RBMstart(self, num_visible, num_hidden):
        self.num_hidden = num_hidden
        self.num_visible = num_visible
        self.debug_print = True

        # Initialize a weight matrix, of dimensions (num_visible x num_hidden), using
        # a uniform distribution between -sqrt(6. / (num_hidden + num_visible))
        # and sqrt(6. / (num_hidden + num_visible)). One could vary the
        # standard deviation by multiplying the interval with appropriate value.
        # Here we initialize the weights with mean 0 and standard deviation 0.1.
        # Reference: Understanding the difficulty of training deep feedforward
        # neural networks by Xavier Glorot and Yoshua Bengio
        np_rng = np.random.RandomState(1234)

        self.weights = np.asarray(np_rng.uniform(
                low=-0.1 * np.sqrt(6. / (num_hidden + num_visible)),
                            high=0.1 * np.sqrt(6. / (num_hidden + num_visible)),
                            size=(num_visible, num_hidden)))


        # Insert weights for the bias units into the first row and first column.
        self.weights = np.insert(self.weights, 0, 0, axis = 0)
        self.weights = np.insert(self.weights, 0, 0, axis = 1)

    def train(self, data, max_epochs = 1000, learning_rate = 0.1):
        """
        Train the machine.
        Parameters
        ----------
        data: A matrix where each row is a training example consisting of the states of visible units.
        """

        num_examples = data.shape[0]

        # Insert bias units of 1 into the first column.
        data = np.insert(data, 0, 1, axis = 1)

        for epoch in range(max_epochs):
            # Clamp to the data and sample from the hidden units.
            # (This is the "positive CD phase", aka the reality phase.)
            pos_hidden_activations = np.dot(data, self.weights)
            pos_hidden_probs = self._logistic(pos_hidden_activations)
            pos_hidden_probs[:,0] = 1 # Fix the bias unit.
            pos_hidden_states = pos_hidden_probs > np.random.rand(num_examples, self.num_hidden + 1)
            # Note that we're using the activation *probabilities* of the hidden states, not the hidden states
            # themselves, when computing associations. We could also use the states; see section 3 of Hinton's
            # "A Practical Guide to Training Restricted Boltzmann Machines" for more.
            pos_associations = np.dot(data.T, pos_hidden_probs)

            # Reconstruct the visible units and sample again from the hidden units.
            # (This is the "negative CD phase", aka the daydreaming phase.)
            neg_visible_activations = np.dot(pos_hidden_states, self.weights.T)
            neg_visible_probs = self._logistic(neg_visible_activations)
            neg_visible_probs[:,0] = 1 # Fix the bias unit.
            neg_hidden_activations = np.dot(neg_visible_probs, self.weights)
            neg_hidden_probs = self._logistic(neg_hidden_activations)
            # Note, again, that we're using the activation *probabilities* when computing associations, not the states
            # themselves.
            neg_associations = np.dot(neg_visible_probs.T, neg_hidden_probs)

            # Update weights.
            self.weights += learning_rate * ((pos_associations - neg_associations) / num_examples)

            error = np.sum((data - neg_visible_probs) ** 2)
            if self.debug_print:
                print("Epoch %s: error is %s" % (epoch, error))

    def run_visible(self, data):
        """
        Assuming the RBM has been trained (so that weights for the network have been learned),
        run the network on a set of visible units, to get a sample of the hidden units.

        Parameters
        ----------
        data: A matrix where each row consists of the states of the visible units.

        Returns
        -------
        hidden_states: A matrix where each row consists of the hidden units activated from the visible
        units in the data matrix passed in.
        """

        num_examples = data.shape[0]

        # Create a matrix, where each row is to be the hidden units (plus a bias unit)
        # sampled from a training example.
        hidden_states = np.ones((num_examples, self.num_hidden + 1))

        # Insert bias units of 1 into the first column of data.
        data = np.insert(data, 0, 1, axis = 1)

        # Calculate the activations of the hidden units.
        hidden_activations = np.dot(data, self.weights)
        # Calculate the probabilities of turning the hidden units on.
        hidden_probs = self._logistic(hidden_activations)
        m = hidden_probs.argmax()
        # Turn the hidden units on with their specified probabilities.
        hidden_states[:,:] = hidden_probs > np.random.rand(num_examples, self.num_hidden + 1)
        # Always fix the bias unit to 1.
        # hidden_states[:,0] = 1

        # Ignore the bias units.
        hidden_states = hidden_states[:,1:]
        return hidden_states

    # TODO: Remove the code duplication between this method and `run_visible`?
    def run_hidden(self, data):
        """
        Assuming the RBM has been trained (so that weights for the network have been learned),
        run the network on a set of hidden units, to get a sample of the visible units.
        Parameters
        ----------
        data: A matrix where each row consists of the states of the hidden units.
        Returns
        -------
        visible_states: A matrix where each row consists of the visible units activated from the hidden
        units in the data matrix passed in.
        """

        num_examples = data.shape[0]

        # Create a matrix, where each row is to be the visible units (plus a bias unit)
        # sampled from a training example.
        visible_states = np.ones((num_examples, self.num_visible + 1))

        # Insert bias units of 1 into the first column of data.
        data = np.insert(data, 0, 1, axis = 1)

        # Calculate the activations of the visible units.
        visible_activations = np.dot(data, self.weights.T)
        # Calculate the probabilities of turning the visible units on.
        visible_probs = self._logistic(visible_activations)
        # Turn the visible units on with their specified probabilities.
        visible_states[:,:] = visible_probs > np.random.rand(num_examples, self.num_visible + 1)
        # Always fix the bias unit to 1.
        # visible_states[:,0] = 1

        # Ignore the bias units.
        visible_states = visible_states[:,1:]
        return visible_states

    def daydream(self, num_samples):
        """
        Randomly initialize the visible units once, and start running alternating Gibbs sampling steps
        (where each step consists of updating all the hidden units, and then updating all of the visible units),
        taking a sample of the visible units at each step.
        Note that we only initialize the network *once*, so these samples are correlated.
        Returns
        -------
        samples: A matrix, where each row is a sample of the visible units produced while the network was
        daydreaming.
        """

        # Create a matrix, where each row is to be a sample of of the visible units
        # (with an extra bias unit), initialized to all ones.
        samples = np.ones((num_samples, self.num_visible + 1))

        # Take the first sample from a uniform distribution.
        samples[0,1:] = np.random.rand(self.num_visible)

        # Start the alternating Gibbs sampling.
        # Note that we keep the hidden units binary states, but leave the
        # visible units as real probabilities. See section 3 of Hinton's
        # "A Practical Guide to Training Restricted Boltzmann Machines"
        # for more on why.
        for i in range(1, num_samples):
            visible = samples[i-1,:]

            # Calculate the activations of the hidden units.
            hidden_activations = np.dot(visible, self.weights)
            # Calculate the probabilities of turning the hidden units on.
            hidden_probs = self._logistic(hidden_activations)
            # Turn the hidden units on with their specified probabilities.
            hidden_states = hidden_probs > np.random.rand(self.num_hidden + 1)
            # Always fix the bias unit to 1.
            hidden_states[0] = 1

            # Recalculate the probabilities that the visible units are on.
            visible_activations = np.dot(hidden_states, self.weights.T)
            visible_probs = self._logistic(visible_activations)
            visible_states = visible_probs > np.random.rand(self.num_visible + 1)
            samples[i,:] = visible_states

        # Ignore the bias units (the first column), since they're always set to 1.
        return samples[:,1:]

    def _logistic(self, x):
        return 1.0 / (1 + np.exp(-x))


# starts from here
def recommender_related(rec_for):
    st = Student.objects.all()  # TODO: Change this to total number of students in the db
    count = 0
    for s in st:
        count = count + 1
    users = count
    items = 19  # TODO: Change this to total number of courses in the db
    recommend_data = open("/Users/gautam/Desktop/IntelliStudy/grades.csv","w") # TODO: Change this address get grades from scores and store into a csv and avg based on courses
    courses = Course.objects.all()
    students = Student.objects.all()
    for c in courses:
        for student in students:
            sc = Score.objects.filter(Q(unique_id=student, content_id=Content.objects.filter(Q(course_id=c)))).aggregate(Avg('marks')).values()
            recommend_data.write(str(student.unique_id.pk) + "," + str(c.pk) + "," + str(sc) + "\n")
    recommend_data.close()
    high1, high2, low1, low2 = predictRating(recommend_data, users, items, rec_for)
    return high1, high2, low1, low2


def readingFile(filename):
    f = open(filename,"r")
    data = []
    for row in f:
        r = row.split(',')
        e = [int(r[0]), int(r[1]), int(r[2])]
        data.append(e)
    return data


def predictRating(recommend_data, users, items, rec_for):
    M, sim_user = crossValidation(recommend_data, users, items)
    pred_low1 = 10
    pred_low2 = 10
    pred_high1 = 0
    pred_high2 = 0
    f = open("/Users/gautam/Desktop/IntelliStudy/toBeGraded.csv","r")  # TODO: Change this address to the courses not enrolled
    #f = open(sys.argv[2],"r")
    items = Enroll.objects.filter(Q(unique_id_id=user))
    toBeRated = {"user":[], "item":[]}
    for i in items:
        toBeRated["item"].append(int(i.pk))
        toBeRated["user"].append(rec_for)

    f.close()

    pred_rate = []

    #fw = open('result1.csv','w')
    fw_w = open('/Users/gautam/Desktop/IntelliStudy/result1.csv','w')  # TODO: Change this to return the results

    l = len(toBeRated["user"])
    for e in range(l):
        user = toBeRated["user"][e]
        item = toBeRated["item"][e]

        pred = 5.0

        #user-based
        if np.count_nonzero(M[user-1]):
            sim = sim_user[user-1]
            ind = (M[:,item-1] > 0)
            #ind[user-1] = False
            normal = np.sum(np.absolute(sim[ind]))
            if normal > 0:
                pred = np.dot(sim,M[:,item-1])/normal

        if pred < 0:
            pred = 0

        if pred > 10:
            pred = 10

        pred_rate.append(pred)

        if(pred<pred_low1):
            pred_low1=pred
            low1 = item
        elif (pred<pred_low2):
            pred_low2=pred
            low2 = item

        if (pred > pred_high1):
            pred_high1 = pred
            high1 = item
        elif (pred > pred_high2):
            pred_high2 = pred
            high2 = item

        print (str(user) + "," + str(item) + "," + str(pred))
        #fw.write(str(user) + "," + str(item) + "," + str(pred) + "\n")
        fw_w.write(str(item) + "," + str(pred) + "\n")                      #   this is how you make csv

    #fw.close()
    fw_w.close()
    return high1, high2, low1, low2

def crossValidation(data, users, items):
    k_fold = KFold(n=len(data), n_folds=10)

    Mat = np.zeros((users,items))
    for e in data:
        Mat[e[0]-1][e[1]-1] = e[2]

    sim_user_cosine, sim_user_jaccard, sim_user_pearson = similarity_user(Mat, users, items)

    rmse_cosine = []
    rmse_jaccard = []
    rmse_pearson = []

    for train_indices, test_indices in k_fold:
        train = [data[i] for i in train_indices]
        test = [data[i] for i in test_indices]

        M = np.zeros((users,items))

        for e in train:
            M[e[0]-1][e[1]-1] = e[2]

        true_rate = []
        pred_rate_cosine = []
        pred_rate_jaccard = []
        pred_rate_pearson = []

        for e in test:
            user = e[0]
            item = e[1]
            true_rate.append(e[2])

            pred_cosine = 5.0
            pred_jaccard = 5.0
            pred_pearson = 5.0

            #user-based
            if np.count_nonzero(M[user-1]):
                sim_cosine = sim_user_cosine[user-1]
                sim_jaccard = sim_user_jaccard[user-1]
                sim_pearson = sim_user_pearson[user-1]
                ind = (M[:,item-1] > 0)
                #ind[user-1] = False
                normal_cosine = np.sum(np.absolute(sim_cosine[ind]))
                normal_jaccard = np.sum(np.absolute(sim_jaccard[ind]))
                normal_pearson = np.sum(np.absolute(sim_pearson[ind]))
                if normal_cosine > 0:
                    pred_cosine = np.dot(sim_cosine,M[:,item-1])/normal_cosine

                if normal_jaccard > 0:
                    pred_jaccard = np.dot(sim_jaccard,M[:,item-1])/normal_jaccard

                if normal_pearson > 0:
                    pred_pearson = np.dot(sim_pearson,M[:,item-1])/normal_pearson

            if pred_cosine < 0:
                pred_cosine = 0

            if pred_cosine > 10:
                pred_cosine = 10

            if pred_jaccard < 0:
                pred_jaccard = 0

            if pred_jaccard > 10:
                pred_jaccard = 10

            if pred_pearson < 0:
                pred_pearson = 0

            if pred_pearson > 10:
                pred_pearson = 10

            print (str(user) + "\t" + str(item) + "\t" + str(e[2]) + "\t" + str(pred_cosine) + "\t" + str(pred_jaccard) + "\t" + str(pred_pearson))
            pred_rate_cosine.append(pred_cosine)
            pred_rate_jaccard.append(pred_jaccard)
            pred_rate_pearson.append(pred_pearson)

        rmse_cosine.append(sqrt(mean_squared_error(true_rate, pred_rate_cosine)))
        rmse_jaccard.append(sqrt(mean_squared_error(true_rate, pred_rate_jaccard)))
        rmse_pearson.append(sqrt(mean_squared_error(true_rate, pred_rate_pearson)))

        print (str(sqrt(mean_squared_error(true_rate, pred_rate_cosine))) + "\t" + str(sqrt(mean_squared_error(true_rate, pred_rate_jaccard))) + "\t" + str(sqrt(mean_squared_error(true_rate, pred_rate_pearson))))
        #raw_input()

    #print sum(rms) / float(len(rms))
    rmse_cosine = sum(rmse_cosine) / float(len(rmse_cosine))
    rmse_pearson = sum(rmse_pearson) / float(len(rmse_pearson))
    rmse_jaccard = sum(rmse_jaccard) / float(len(rmse_jaccard))

    print (str(rmse_cosine) + "\t" + str(rmse_jaccard) + "\t" + str(rmse_pearson))

    f_rmse = open("rmse_user.txt","w")
    f_rmse.write(str(rmse_cosine) + "\t" + str(rmse_jaccard) + "\t" + str(rmse_pearson) + "\n")

    rmse = [rmse_cosine, rmse_jaccard, rmse_pearson]
    req_sim = rmse.index(min(rmse))

    print (req_sim)
    f_rmse.write(str(req_sim))
    f_rmse.close()

    if req_sim == 0:
        sim_mat_user = sim_user_cosine

    if req_sim == 1:
        sim_mat_user = sim_user_jaccard

    if req_sim == 2:
        sim_mat_user = sim_user_pearson

    #predictRating(Mat, sim_mat_user)
    return Mat, sim_mat_user

def similarity_user(data, users, items):
    user_similarity_cosine = np.zeros((users,users))
    user_similarity_jaccard = np.zeros((users,users))
    user_similarity_pearson = np.zeros((users,users))
    for user1 in range(users):
        print (user1)
        for user2 in range(users):
            if np.count_nonzero(data[user1]) and np.count_nonzero(data[user2]):
                user_similarity_cosine[user1][user2] = 1-scipy.spatial.distance.cosine(data[user1],data[user2])
                user_similarity_jaccard[user1][user2] = 1-scipy.spatial.distance.jaccard(data[user1],data[user2])
                try:
                    if not math.isnan(scipy.stats.pearsonr(data[user1],data[user2])[0]):
                        user_similarity_pearson[user1][user2] = scipy.stats.pearsonr(data[user1],data[user2])[0]
                    else:
                        user_similarity_pearson[user1][user2] = 0
                except:
                    user_similarity_pearson[user1][user2] = 0
    return user_similarity_cosine, user_similarity_jaccard, user_similarity_pearson
