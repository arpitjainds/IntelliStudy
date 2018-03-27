from django.db import models
from django.contrib.auth.models import User


class Constants:
    USER_CHOICES = (
        ('student', 'student'),
        ('mentor', 'mentor'),
    )

    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    CONTENT_TYPE = (
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
    )

    LEVEL = (
        ('beginner', 'beginner'),
        ('intermediate', 'intermediate'),
        ('advanced', 'advanced'),
    )
    JOB_TYPE = (
        ('Intern', 'Intern'),
        ('Entry level (0-2 yrs)', 'Entry level (0-2 yrs)'),
        ('Mid level (2+ yrs)', 'Mid level (2+ yrs)'),
        ('Manager', 'Manager'),
        ('Executive', 'Executive'),
        ('Not Applicable', 'Not Applicable'),
    )
    EDUCATION_LEVEL = (
        ('Below High School', 'Below High School'),
        ('High School', 'High School'),
        ('Bachelor Degree', 'Bachelor Degree'),
        ('Master Degree', 'Master Degree'),
        ('Doctrate Degree', 'Doctrate Degree'),
    )


class ExtraInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=2, choices=Constants.SEX_CHOICES, default='M')
    date_of_birth = models.DateField(null=True)
    profile_picture = models.ImageField(null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=Constants.USER_CHOICES,
                                 default='student')
    job = models.CharField(max_length=20, choices=Constants.JOB_TYPE,
                           null=True, blank=True)
    qualification = models.CharField(max_length=40, choices=Constants.EDUCATION_LEVEL,
                                     null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.user)


class Student(models.Model):
    unique_id = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE, primary_key=True)
    career_goal = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.unique_id.id)


class Mentor(models.Model):
    mentor_id = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return '{}'.format(self.mentor_id.id)


class Course(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(default='', max_length=1000, blank=True, null=True)
    course_picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class Content(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    level = models.CharField(max_length=20, choices=Constants.LEVEL, default='intermediate')
    content_picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.course_id.id, self.name)


class Question(models.Model):
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=Constants.LEVEL, default='intermediate')
    question = models.TextField(max_length=4000, null=True, blank=True)
    answer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.content_id.course_id.id, self.content_id)


class Option(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=100, null=True, blank=True)


class Career(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    career_picture = models.ImageField(null=True, blank=True)


class Has(models.Model):
    career_id = models.ForeignKey(Career, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=Constants.LEVEL, default='intermediate')
    order = models.IntegerField(default=1)


class Enroll(models.Model):
    unique_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    feedback = models.TextField(default='', max_length=1000, blank=True, null=True)


class Score(models.Model):
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE)
    unique_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks = models.IntegerField(default=0)


class Group(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)


class Contain(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    unique_id = models.ForeignKey(Student, on_delete=models.CASCADE)


class Manage(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    mentor_id = models.ForeignKey(Mentor, on_delete=models.CASCADE)


class Message(models.Model):
    message = models.TextField(default='', max_length=8000, blank=True, null=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    unique_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)


class Peer(models.Model):
    unique_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    question = models.TextField(max_length=4000, null=True, blank=True)
    answer = models.TextField(max_length=4000, null=True, blank=True)


class Progress(models.Model):
    enroll_id = models.ForeignKey(Enroll, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Constants.CONTENT_TYPE, default='ONGOING')


class File(models.Model):
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE)
    mentor_id = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    file = models.FileField()
    name = models.CharField(max_length=100)
