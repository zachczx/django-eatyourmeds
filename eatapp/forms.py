from django import forms
from .models import CourseInfo, DoseInfo, Patient
# crispy forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field,  Submit, Reset, Div, Button
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.urls import reverse_lazy, reverse


class BetaCourseForm(forms.ModelForm):
    class Meta:
        fields = ['medicine', 'interval',
                  'course_duration', 'course_start', 'patient']
        model = CourseInfo
        labels = {
            'interval': 'Number of hours in between each dose:',
            'course_duration': 'Number of days to take the medicine:',
            'course_start': 'Date/time you first ate the medicine:',
            "patient": "Who's eating the medicine?",
        }

    def __init__(self, user=None, *args, **kwargs):
        self.patient = Patient.objects.filter(parent=user)
        super(BetaCourseForm, self).__init__(*args, **kwargs)
        self.fields['patient'].queryset = self.patient
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Hi {{form_user}}! Let\'s start with some details of your medicine:',
            ),
            Div(
                Div('medicine', css_class='col-sm-6'),
                Div('patient', css_class='col-sm-6'),
                css_class='row pt-3 pb-4',
            ),
            Div(
                Div(AppendedText('interval', 'hours'), css_class='col-sm-6'),
                Div(AppendedText('course_duration', 'days'), css_class='col-sm-6'),
                css_class='row pb-4',
            ),
            Div(
                Field('course_start', id='id_course_start'),
                css_class='row pb-4',
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='text-white fw-bold'),
                Reset('cancel', 'Cancel', css_class='btn btn-outline-secondary'),
            ),
        )


class BetaDoseForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = DoseInfo


class BetaDoseHtmxForm(forms.ModelForm):
    class Meta:
        fields = ['dose_timing']
        model = DoseInfo


class BetaDoseAutoForm(forms.ModelForm):
    class Meta:
        fields = []
        model = DoseInfo


class BetaUserCreateForm(UserCreationForm):

    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                'username',
                css_class='row pb-4',
            ),
            Div(
                'email',
                css_class='row pb-4',
            ),
            Div(
                Div(
                    AppendedText('password1', mark_safe(
                        '<i class="bi bi-eye-slash" id="togglePassword1"></i>')),
                    css_class='col-sm-6',
                    id='#id_password1',
                ),
                Div(
                    AppendedText('password2', mark_safe(
                        '<i class="bi bi-eye-slash" id="togglePassword2"></i>')),
                    css_class='col-sm-6',
                    id='#id_password2',
                ),
                css_class='row pb-4',
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='text-white fw-bold'),
                Reset('cancel', 'Cancel', css_class='btn btn-outline-secondary'),
            ),
        )


class BetaLoginForm(AuthenticationForm):

    class Meta:
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                css_class='row',
            ),
            Div(
                'username',
                css_class='col pb-4',
            ),
            Div(
                css_class='row',
            ),
            Div(
                Div(
                    AppendedText('password', mark_safe(
                        '<i class="bi bi-eye-slash" id="togglePassword1"></i>')),
                ),
                css_class='col pb-4',
            ),
            FormActions(
                Submit('submit', 'Login', css_class='text-white fw-bold'),
                Reset('cancel', 'Cancel', css_class='btn btn-outline-secondary'),
            ),
        )


class BetaPatientUpdateForm(forms.ModelForm):

    name = forms.CharField(required=True)

    class Meta:
        model = Patient
        fields = ['name', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Div(
                    css_class='col-2',
                ),
                Div(
                    Field('name', placeholder='Add a name'),
                    css_class='col-4',
                ),
                Div(
                    Submit('submit', 'Add Kid', css_class='text-white fw-bold'),
                    Reset('cancel', 'Cancel',
                          css_class='btn btn-outline-secondary'),
                    css_class='col-4',
                ),
                Div(
                    css_class='col-2',
                ),
                css_class="row g-2",
            )
        )
