from __future__ import print_function
import random
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
    r = RBM()
    q = r.RBMx(s)
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
    print(password)
    extrainfo.job = job
    extrainfo.qualification = qualification
    extrainfo.profile_picture = request.POST.get("profile_pic")
    print(extrainfo)
    extrainfo.save()

    if password is not "":
        user.set_password(password)
        user.save()

    # if 'change_pic' in request.POST:
    #     pic = request.POST.get("profile_pic")
    #     extrainfo.profile_picture = pic
    #     extrainfo.save()

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



#_________________RBM for recommending course according to career and courses taken by student__________________#

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

#_________________________________END______________________________________#

