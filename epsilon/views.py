import random
import numpy as np
import datetime
import pytz
from dateutil import parser


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q
from .models import (Course, Enroll, Student, Mentor, Question, ExtraInfo, Content, Manage, Score,
                     File, Option, Contain, Group, Career, Has)
from .forms import AddSubtopic


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
    courses = Course.objects.all()
    career = Career.objects.all()
    context = {'courses': courses, 'career': career}
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
