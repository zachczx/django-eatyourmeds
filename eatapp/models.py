from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.

medicine_choices = [
    ('Ibuprofen', 'Ibuprofen'),
    ('Paracetamol', 'Paracetamol'),
    ('Zyrtec', 'Zyrtec'),
    ('Cetirizine', 'Cetirizine'),
    ('Promethazine', 'Promethazine'),
    ('Ivy Leaf Extract', 'Ivy Leaf Extract'),
]

# rec_interval, description, used for, sideeffects, brandname
# medicine_info = (
#     "Cetirizine", [4, 
#                    "Cetirizine is an antihistamine used to relieve allergy symptoms such as watery eyes, runny nose, itching eyes/nose, sneezing, hives, and itching. It works by blocking a certain natural substance (histamine) that your body makes during an allergic reaction. Cetirizine does not prevent hives or prevent/treat a serious allergic reaction (such as anaphylaxis).",
#                    "relieve allergy symptoms such as watery eyes, runny nose, itching eyes/nose, sneezing, hives, and itching.",
#                    "Allergy symptoms such as watery eyes, runny nose, itching eyes/nose, sneezing, hives, and itching",	"Drowsiness, tiredness, and dry mouth may occur. Stomach pain may also occur, especially in children. If any of these effects last or get worse, tell your doctor or pharmacist promptly",	
#                    "Zyrtec"],
#     "Paracetamol", [6,
#                     "Paracetamol is an analgesic and antipyretic drug that is used to temporarily relieve mild-to-moderate pain and fever. It is commonly included as an ingredient in cold and flu medications and is also used on its own.",
#                     "Mild to moderate pain (from headaches, menstrual periods, toothaches, backaches, osteoarthritis, or cold/flu aches and pains) and to reduce fever.",
#                     "Usually has no side effects.",
#                     "Panadol"],
#     "Promethazine", [6,
#                     "Promethazine is an antihistamine and works by blocking a certain natural substance (histamine) that your body makes during an allergic reaction. Its other effects (such as anti-nausea, calming, pain relief) may work by affecting other natural substances (such as acetylcholine) and by acting directly on certain parts of the brain.",
#                     "Prevent and treat nausea and vomiting related to certain conditions (such as before/after surgery, motion sickness). It is also used to treat allergy symptoms such as rash, itching, and runny nose.",	
#                     "Drowsiness, dizziness, constipation, blurred vision, or dry mouth may occur. If any of these effects last or get worse, tell your doctor.",
#                     "Promethazine"],
#     "Ivy Leaf Extract", [8,
#                     "Ivy Leaf extract might improve lung function in people with breathing difficulty. English ivy might also have antioxidant effects.	Ivy Leaf extract might help thin mucus in the airways.",	
#                     "Nausea, vomiting and diarrhea",	
#                     "Prospan, Abrilar"],
# )

class MedicalInfo(models.Model):
    medicine = models.CharField(max_length=50, choices=medicine_choices)
    rec_interval = models.IntegerField(null=False)
    description = models.TextField(max_length=500)
    used_for = models.TextField(max_length=500, default="")
    sideeffects = models.TextField(max_length=500)
    brandname = models.TextField(max_length=500, default="", null=True)

    def __str__(self):
        return self.medicine


class EatModel(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    medicine = models.ForeignKey(
        MedicalInfo, on_delete=models.SET_NULL, null=True)
    interval = models.IntegerField(default=4)
    last_fed = models.DateTimeField(default=datetime.now)
    second_dose = models.DateTimeField(default=None, null=True)
    third_dose = models.DateTimeField(default=None, null=True)
    fourth_dose = models.DateTimeField(default=None, null=True)
    fifth_dose = models.DateTimeField(default=None, null=True)
    remarks = models.TextField(max_length=140, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_second_dose(self):
        a = self.last_fed + timedelta(hours=self.interval)
        return a

    @property
    def get_third_dose(self):
        b = self.last_fed + timedelta(hours=self.interval) * 2
        return b

    @property
    def get_fourth_dose(self):
        c = self.last_fed + timedelta(hours=self.interval) * 3
        return c

    @property
    def get_fifth_dose(self):
        d = self.last_fed + timedelta(hours=self.interval) * 4
        return d

    def save(self, *args, **kwargs):
        self.second_dose = self.get_second_dose
        self.third_dose = self.get_third_dose
        self.fourth_dose = self.get_fourth_dose
        self.fifth_dose = self.get_fifth_dose
        super(EatModel, self).save(*args, **kwargs)

    class Meta:
        ordering = ['complete']  # ordering in descending just do -complete


class Patient(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, default=None)
    parent = models.ForeignKey(
        User, blank=True, null=True, default=None, on_delete=models.CASCADE)
    hehe = models.CharField(max_length=50, blank=True, null=True, default=None)

    def __str__(self):
        return str(self.name)


class CourseInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    medicine = models.ForeignKey(
        MedicalInfo, on_delete=models.SET_NULL, null=True)
    interval = models.IntegerField(default=4)
    course_duration = models.IntegerField(default=3)
    course_start = models.DateTimeField(default=datetime.now)
    complete = models.BooleanField(default=False)
    course_created = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class DoseInfo(models.Model):
    courseinfo = models.ForeignKey(
        CourseInfo, on_delete=models.CASCADE, default='')
    dose_timing = models.DateTimeField(default=datetime.now)
    dose_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['dose_timing']

    def __str__(self):
        return str(self.id)
