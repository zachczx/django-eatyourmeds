# from typing import Any
from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
# from django.http import HttpResponse

# from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
# new django 5.0 logout # to login right after creating account
from django.contrib.auth import login, logout

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy, reverse
from .models import EatModel, MedicalInfo

# beta version stuff
from .models import CourseInfo, DoseInfo, Patient
from .forms import BetaCourseForm, BetaDoseForm, BetaDoseHtmxForm, BetaDoseAutoForm, BetaUserCreateForm, BetaLoginForm, BetaPatientUpdateForm
from django.views.generic import ListView, DetailView
from .utils import Calendar
from django.utils.safestring import mark_safe
import copy
from django.contrib.auth.decorators import login_required

# caching
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from utils.mixins import CacheMixin

# localtime to do subtraction
from django.utils.timezone import datetime, timedelta, localtime

# Create your views here.


class EatLogin(LoginView):
    authentication_form = BetaLoginForm
    template_name = 'eatapp/registration/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('betamain')


def logout_view(request):
    logout(request)
    return redirect('betamain')
    # Redirect to a success page.


class EatRegister(FormView):
    template_name = 'eatapp/registration/register.html'
    form_class = BetaUserCreateForm
    success_url = reverse_lazy('betapatientupdate')
    context_object_name = 'form'

    def form_valid(self, form):
        user = form.save()  # this is user cos we are working with usercreationform
        if user != None:
            login(self.request, user)
        return super(EatRegister, self).form_valid(form)

    # validate and then redirect using login()
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            # import redirect
            return redirect('betamain')
        return super(EatRegister, self).get(*args, **kwargs)


class EatCreate(LoginRequiredMixin, CreateView):
    model = EatModel
    fields = ['medicine', 'remarks', 'last_fed', 'interval', 'complete']
    success_url = reverse_lazy('newlist')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EatCreate, self).form_valid(form)


class BetaMain(LoginRequiredMixin, ListView):
    cache_timeout = 90
    template_name = 'eatapp/betamain.html'
    model = CourseInfo
    context_object_name = 'courseinfo'

    def get_queryset(self):
        return CourseInfo.objects.filter(user=self.request.user).prefetch_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_id = CourseInfo.objects.filter(
            user=self.request.user).values_list('id', flat=True)
        # qs_id2 = CourseInfo.objects.filter(user=self.request.user).values_list('id', flat=True)
        upcomingoneday = localtime() + timedelta(hours=6)  # for main page content display
        context['doseinfo'] = DoseInfo.objects.filter(courseinfo_id__in=qs_id).filter(dose_timing__gte=localtime(
            # for main page content display
        )).filter(dose_timing__lte=upcomingoneday).select_related()
        qs_dose = DoseInfo.objects.filter(courseinfo_id__in=qs_id)

        # convert queryset dict to dict with list inside
        qs_id_list = {}
        for i in qs_id:
            qs_id_list[i] = []

        newlist = copy.deepcopy(qs_id_list)
        finishedlist = copy.deepcopy(qs_id_list)
        progress = copy.deepcopy(qs_id_list)
        timenow = localtime()

        for item in qs_dose:
            # grab all relevant items based on courseinfo_id
            if item.courseinfo_id in qs_id:
                newlist[item.courseinfo_id].append(item.dose_timing)
            # grab the items that were in the past
            if item.courseinfo_id in qs_id and item.dose_timing < timenow:
                finishedlist[item.courseinfo_id].append(item.dose_timing)

        # do division
        for key in progress:
            if len(newlist[key]) == 0:
                progress[key] = 0
            else:
                progress[key] = round(
                    (len(finishedlist[key])/len(newlist[key])) * 100)

        context['progress'] = progress

        return context


class BetaCreateCourse(LoginRequiredMixin, CreateView):
    template_name = 'eatapp/beta_create_course.html'
    form_class = BetaCourseForm

    # to auto populate the form user created
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BetaCreateCourse, self).form_valid(form)
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_user'] = self.request.user
        return context
    '''

    def get_form_kwargs(self):
        kwargs = super(BetaCreateCourse, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('betaviewcourse', kwargs={'pk': self.object.id})


'''
def beta_create_course(request):
    form = BetaCreateCourse(request.POST or None)
    
    #if request.method == 'GET':    
    #    return render(request, 'eatapp/htmx_create_dose.html', {'form': form})
    
    if request.method == 'POST':
 
        if form.is_valid():
            #fill in the course info automatically
            filled = form.save(commit=False)
            filled.courseinfo_id = id
            filled.save()
            
    return HttpResponseRedirect('betaviewcourse', kwargs="")
'''


class BetaCreateDose(CreateView):
    template_name = 'eatapp/beta_create_dose.html'
    form_class = BetaDoseForm


class BetaViewCourse(LoginRequiredMixin, ListView):

    model = CourseInfo
    template_name = 'eatapp/beta_view_course.html'
    login_url = 'eatlogin'
    context_object_name = 'courseinfo'

    def get_queryset(self):
        get_qs = CourseInfo.objects.filter(pk=self.kwargs.get('pk'))
        return get_qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        dose_qs = DoseInfo.objects.filter(
            courseinfo_id=self.kwargs.get('pk')).values()
        context['doseinfo'] = dose_qs
        context['htmx_create_dose'] = BetaDoseHtmxForm()

        #### calendar render ####
        dose_dates = DoseInfo.objects.filter(courseinfo_id=self.kwargs.get(
            'pk')).values_list('dose_timing', flat=True)
        # start_timing_calendar = DoseInfo.objects.filter(courseinfo_id=self.kwargs.get('pk')).order_by('dose_timing').values('dose_timing').first()
        if not dose_dates:
            pass
        else:
            start_timing_calendar_month = dose_dates[0].month
            start_timing_calendar_year = dose_dates[0].year
            cal = Calendar(start_timing_calendar_year,
                           start_timing_calendar_month)
            html_cal = cal.formatmonth(withyear=True)
            context['calendar'] = mark_safe(html_cal)
        #### end calendar render ####
        total_doses = dose_qs.count()
        pending_doses = dose_qs.filter(dose_timing__gte=localtime()).count()
        if total_doses == 0:
            context['progress'] = 0
        else:
            context['progress'] = round(
                (total_doses-pending_doses)/total_doses*100)
        return context


class BetaDeleteCourse(LoginRequiredMixin, DeleteView):
    model = CourseInfo
    template_name = 'eatapp/betadelete_p.html'
    fields = "__all__"
    context_object_name = 'courseinfo'
    success_url = reverse_lazy('betamain')


class BetaUpdateCourse(LoginRequiredMixin, UpdateView):
    model = CourseInfo
    template_name = 'eatapp/betaupdatecourse.html'
    fields = "__all__"
    context_object_name = 'courseinfo'

    def get_success_url(self):
        return reverse('betaviewcourse', kwargs={"pk": self.kwargs.get('pk')})


@login_required
def betapatientupdate(request):

    form = BetaPatientUpdateForm()
    patient_list = Patient.objects.filter(
        parent_id=request.user.id).select_related()
    context = {
        'patient_list': patient_list,
        'form': form,
    }
    return render(request, 'eatapp/beta_update_patient.html', context)


def htmx_create_dose(request, id):

    form = BetaDoseHtmxForm(request.POST or None)

    # if request.method == 'GET':
    #    return render(request, 'eatapp/htmx_create_dose.html', {'form': form})

    if request.method == 'POST':
        form.courseinfo = id
        if form.is_valid():
            # fill in the course info automatically
            filled = form.save(commit=False)
            filled.courseinfo_id = id
            filled.save()
            courseinfo = CourseInfo.objects.filter(pk=id)
            doseinfo = DoseInfo.objects.filter(
                courseinfo_id=id).order_by('dose_timing').values()
            htmx_create_dose = BetaDoseHtmxForm()

            context = {
                'courseinfo': courseinfo,
                'doseinfo': doseinfo,
                'form': form,
                'htmx_create_dose': htmx_create_dose,
            }
            return render(request, 'eatapp/htmx_view_dose.html', context)


@require_http_methods(['POST'])
def htmx_create_dose_auto(request, id):

    form = BetaDoseAutoForm(request.POST or None)

    # if request.method == 'GET':
    #    return render(request, 'eatapp/htmx_create_dose.html', {'form': form})

    # generate the dose timings
    qs = CourseInfo.objects.filter(pk=id).values(
        'course_start', 'course_duration', 'interval')
    start_date = qs[0]['course_start']
    course_duration = qs[0]['course_duration']
    interval = qs[0]['interval']

    number_of_doses = int((course_duration * 24)/interval)
    local_time = localtime()

    new_doses = [
        DoseInfo(courseinfo_id=id, dose_timing=start_date,
                 dose_created=local_time),
    ]

    i = 1

    while i < number_of_doses:
        start_date = start_date + timedelta(hours=interval)
        new_doses.append(
            DoseInfo(courseinfo_id=id, dose_timing=start_date, dose_created=local_time))
        i += 1

    if request.method == 'POST':

        if form.is_valid():
            objs = DoseInfo.objects.bulk_create(new_doses)
            url = reverse('betaviewcourse', kwargs={'pk': id})
            return HttpResponseRedirect(url)


@require_http_methods(['DELETE'])
def htmx_delete_course(request, id):
    CourseInfo.objects.filter(id=id).delete()
    courseinfo = CourseInfo.objects.filter(
        user=request.user).prefetch_related()
    qs_id = CourseInfo.objects.filter(user=request.user).values('id')
    upcomingoneday = localtime() + timedelta(hours=6)
    doseinfo = DoseInfo.objects.filter(courseinfo_id__in=qs_id).filter(
        dose_timing__gte=localtime()).filter(dose_timing__lte=upcomingoneday).select_related()
    context = {
        'courseinfo': courseinfo,
        'doseinfo': doseinfo,
    }
    return render(request, "eatapp/partials/betamain_content.html", context)


@require_http_methods(['DELETE'])
def htmx_delete_dose(request, id, doseid):
    DoseInfo.objects.filter(id=doseid).delete()
    courseinfo = CourseInfo.objects.filter(pk=id)
    doseinfo = DoseInfo.objects.filter(
        courseinfo_id=id).order_by('dose_timing').values()
    # qs_id = CourseInfo.objects.filter(user=request.user).values('id')
    context = {
        'courseinfo': courseinfo,
        'doseinfo': doseinfo,
    }
    return render(request, 'eatapp/htmx_view_dose.html', context)


@login_required
def htmx_create_kid(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = BetaPatientUpdateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            profile = form.save(commit=False)
            profile.parent = request.user
            profile.save()

    patient_list = Patient.objects.filter(
        parent_id=request.user.id).select_related()
    context = {
        'patient_list': patient_list,
    }
    return render(request, 'eatapp/htmx_view_kid.html', context)


@login_required
@require_http_methods(['DELETE'])
def htmx_delete_kid(request, kidid):
    Patient.objects.filter(id=kidid).delete()
    patient_list = Patient.objects.filter(
        parent_id=request.user.id).select_related()
    context = {
        'patient_list': patient_list,
    }
    return render(request, 'eatapp/htmx_view_kid.html', context)
