import random


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from .models import (Course, Enroll, Student, Mentor, Question, ExtraInfo, Content, Manage, Score,
                     File, Option, Contain, Group, Career, Has)


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
            return rediect('/epsilon/mdashboard')
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
        contain = Contain.objects.filter(Q(group_id=Group.objects.get(course_id=course),
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
    extrainfo.save()
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
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, "epsilon/editcourse.html", context)


@login_required
def loggedout(request):
    logout(request)
    return redirect('/epsilon')
