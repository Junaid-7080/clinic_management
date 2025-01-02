from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models 
from django.utils.timezone import now





class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, password=None, **extrafields):
        if not username:
            raise ValueError('User must have a username')
        if not password:
            raise ValueError('User must have a password') 
        user=self.model(username=username,**extrafields)
        user.set_password(password)
        user.save()
        return user 

    def create_superuser(self,username,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault('role',1)
        return self.create_user(username, password ,**extra_fields)

ROLE_CHOICE=[
    (1,'Admin'),
    (2,'Receptionist'),
    (3,'Doctor'),
    (4,'Patient')
]

class CustomUser(AbstractBaseUser,PermissionsMixin):
    username=models.CharField(max_length=100,unique=True)
    email=models.EmailField(blank=True,null=True)
    is_active=models.BooleanField(default=True,verbose_name='active')
    is_staff=models.BooleanField(default=False)
    role=models.IntegerField(choices=ROLE_CHOICE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD='username' 
    REQUIRED_FIELDS=[]
    objects=CustomUserManager()

    def _str_(self):
        return self.username
    



class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True) 
    address = models.CharField(max_length=255, null=True, blank=True)
    pat_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    

    is_patient = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"





class ReceptionistProfile(models.Model):
    recp_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE, null=True)
    name = models.TextField(max_length=30)
    contact_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    clinic_name = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Receptionist: {self.clinic_name}"



class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('General Practitioner', 'General Practitioner'),
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Orthopedic', 'Orthopedic'),
        ('Pediatrician', 'Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Radiologist', 'Radiologist')

    ]

    doctor_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100,choices=SPECIALIZATION_CHOICES)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='image/',null=True)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    clinic_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_doctor = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"


class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')
    ]

    SHIFTS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    specialization = models.CharField(max_length=100, choices=Doctor.SPECIALIZATION_CHOICES)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    shifts = models.CharField(max_length=100,null=True ,choices=SHIFTS)
    day = models.CharField(max_length=9, choices=DAYS_OF_WEEK)


    class Meta:
        unique_together = ('doctor', 'day', 'shifts','specialization')

    def _str_(self):
        return f'{self.specialization} - {self.doctor}- {self.shifts})'






class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments", limit_choices_to={'pat_user__role': 4})
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_appointments", limit_choices_to={'doctor_user__role': 3})
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    specialization = models.CharField(max_length=100, choices=Doctor.SPECIALIZATION_CHOICES, null=True)
    shift = models.CharField(max_length=40, null=True)
    token = models.PositiveIntegerField(editable=False, null=True)

    class Meta:
        unique_together = ('doctor', 'date', 'schedule', 'patient')

    def save(self, *args, **kwargs):
        today = now().date()  # Get today's date
        if not self.id:  # Only if the object is being created
            # Get the max token for the same schedule and date
            last_token = Appointment.objects.filter(date=today, schedule=self.schedule) \
                                            .order_by('-token') \
                                            .first()

            # Assign token incrementally based on the last token for this schedule
            self.token = (last_token.token + 1) if last_token else 1

        super().save(*args, **kwargs)


class Medicine(models.Model):
    name = models.CharField(max_length=255)

    def _str_(self):
        return self.name

class Dose(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dose = models.CharField(max_length=255)  # Example: '500mg'
    cost = models.FloatField()

    def _str_(self):
        return f"{self.medicine.name} - {self.dose}"
    
class Test(models.Model):
    name = models.CharField(max_length=255)
    cost = models.FloatField()

    def _str_(self):
        return self.name




class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    illness_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    date = models.DateField(null=True)
    def _str_(self):
        return f"Prescription for {self.patient} by {self.doctor} on {self.date}"



class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    dose = models.ForeignKey(Dose, on_delete=models.CASCADE)
    per_day = models.IntegerField()
    duration_days = models.IntegerField()

class PrescriptionTest(models.Model):
    Prescription = models.ForeignKey(Prescription,models.CASCADE)
    test = models.ForeignKey(Test,models.CASCADE)


    



   


    


