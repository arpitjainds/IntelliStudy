from django import forms
from .models import ExtraInfo

class AddInformation(forms.Form):
    fname = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                            label="fname")

    lname = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                            label="lname")

    username = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                               label="username")

    sex = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'field'}),
                          label="gender")

    email = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                            label="email")

    password = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                               label="password")

    cpass = forms.CharField(widget=forms.TextInput(attrs={'max_length': 2,
                                                         'class': 'form-control'}),
                            label="password")

    date_of_birth = forms.DateField(label='exampledate1', widget=forms.widgets.DateInput(attrs={'class': 'form-control'}))

    # profile_picture = forms.ImageField()                                                                  

    job = forms.CharField(widget=forms.TextInput(attrs={'class': 'custom-select'}),
                          label="exampleselect2")
    
    qualification = forms.CharField(widget=forms.TextInput(attrs={'max_length': 40,
                                                         'class': 'custom-select'}),
                                    label="exampleselect3")

class AddSubtopic(forms.ModelForm):
    class Meta:
        model = File
        fields = ('content_id','mentor_id','file', 'name',)