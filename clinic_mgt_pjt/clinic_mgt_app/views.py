from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
import json
from .models import CustomUser
from django.http import HttpResponse
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from itertools import groupby
from operator import attrgetter
    



# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST.get('Name')  # Match the field name in HTML
        email = request.POST.get('email')
        password1 = request.POST.get('password')  # Match the field name in HTML
        password2 = request.POST.get('confirm_password')  # Match the field name in HTML
        role = request.POST.get('role')

        if password1 == password2:
            if CustomUser.objects.filter(username=username).exists():
                return HttpResponse("Username already exists. Please choose a different one.")
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    role=role
                )
                user.save()
                return redirect('login')
            except ValueError as e:
                return HttpResponse(str(e))
        else:
            return HttpResponse("Passwords do not match.")
    
    filter_ROLE_CHOICE = [(id, name) for id, name in ROLE_CHOICE if name != 'Admin']
    context = {'role_choices': filter_ROLE_CHOICE}
    return render(request, 'register.html', context)



    
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            # Check if user is approved or an admin
            if user.is_approved or user.role == 1:
                login(request, user)
                # Redirect based on user role
                if user.role == 1:
                    return redirect('admin_home')
                elif user.role == 2:
                        if ReceptionistProfile.objects.filter(recp_user=user).exists():
                            return redirect('recep_home')
                        else:
                            return redirect('create_receptionist_profile')
                elif user.role == 3:
                    if Doctor.objects.filter(doctor_user=user).exists():
                        return redirect('doctor_home')
                    else:
                        return redirect('create_doctor')
                    
                elif user.role == 4:
                    if Patient.objects.filter(pat_user=user).exists():
                        return redirect('patient_home')
                    else:
                        return redirect('patient_create')
                    
                    

                    
    
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def not_login(request):
    return render(request,'not_login.html')

def admin_home(request):
    main = CustomUser.objects.all()
    context ={'main':main}
    return render (request,'admin_home.html',context)

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors_list.html', {'doctors': doctors})

def delete_doctor(request):
    if request.method == "POST":
        doctor_id = request.POST.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        doctor.delete()
        return redirect('doctor_list')
    
def patient_list(request):
    patients = Patient.objects.all()  # Fetch all patient records
    context = {
        'patients': patients
    }
    return render(request, 'patients_list.html', context)

def delete_patient(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        patient.delete()
        return redirect('patient_list')
    

def receptionist_list(request):
    receptionists = ReceptionistProfile.objects.all()  
    context = {
        'receptionists': receptionists
    }
    return render(request, 'receptionists_list.html', context)


def delete_receptionist(request):
    if request.method == "POST":
        receptionist_id = request.POST.get('receptionist_id')
        receptionist = get_object_or_404(ReceptionistProfile, id=receptionist_id)
        receptionist.delete()
        return redirect('receptionist_list')





def recep_home(request):
    # Fetch all doctors
    doctors = Doctor.objects.all()
    
    # Fetch the schedule for each doctor
    schedules = Schedule.objects.all()
    
    try:
        # Fetch receptionist profile for the logged-in user
        receptionist_profile = ReceptionistProfile.objects.get(recp_user=request.user)
    except ReceptionistProfile.DoesNotExist:
        receptionist_profile = None

    # Handle the deletion of a schedule
    if request.method == 'POST' and 'delete_schedule' in request.POST:
        schedule_id = request.POST.get('schedule_id')
        try:
            schedule_to_delete = Schedule.objects.get(id=schedule_id)
            schedule_to_delete.delete()  # Delete the schedule
            return redirect('recep_home')  # Redirect after deletion
        except Schedule.DoesNotExist:
            raise Http404("Schedule not found.")

    # Prepare context for the template
    context = {
        'receptionist_profile': receptionist_profile,
        'doctors': doctors,
        'schedules': schedules,
    }

    return render(request, 'recep_home.html', context)


def create_receptionist_profile(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        clinic_name = request.POST.get('clinic_name')
        emergency_contact = request.POST.get('emergency_contact')

        # Create the ReceptionistProfile
        receptionist_profile = ReceptionistProfile(
            recp_user=request.user,
            name=name,
            contact_number=contact_number,
            address=address,
            clinic_name=clinic_name,
            emergency_contact=emergency_contact,
        )
        receptionist_profile.save()
        
        return redirect('recep_home')

    return render(request, 'recp_pro_crt.html')






def receptionist_profile_detail(request, pk):
    receptionist_profile = ReceptionistProfile.objects.get(recp_user=request.user)
    return render(request, 'receptionist_profile_detail.html', {'receptionist_profile': receptionist_profile})


def edit_receptionist_profile(request, pk):
    # Fetch the existing profile
    receptionist_profile = get_object_or_404(ReceptionistProfile, pk=pk, recp_user=request.user)

    if request.method == 'POST':
        # Update profile fields with form data
        receptionist_profile.name = request.POST.get('name')
        receptionist_profile.contact_number = request.POST.get('contact_number')
        receptionist_profile.address = request.POST.get('address')
        receptionist_profile.clinic_name = request.POST.get('clinic_name')
        receptionist_profile.emergency_contact = request.POST.get('emergency_contact')
        receptionist_profile.save()

        return redirect('recep_home')  # Redirect to the home page or another relevant page

    return render(request, 'recp_pro_edit.html', {'receptionist_profile': receptionist_profile})



def patient_home(request):
    # Retrieve the logged-in patient's profile
    patient = Patient.objects.filter(pat_user=request.user).first()

    if not patient:
        # Redirect to a profile creation or error page if the patient doesn't exist
        return render(request, 'patient_profile_missing.html')

    # Fetch all doctors
    doctors = Doctor.objects.all()

    # Fetch schedules related to the listed doctors
    schedules = Schedule.objects.filter(doctor__in=doctors)

    # Pass data to the template
    context = {
        'patient': patient,
        'doctors': doctors,
        'schedules': schedules,
    }
    return render(request, 'patient_home.html', context)






def patient_create(request):
    if request.method == 'POST':
        # Retrieve data from the form submission
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')


        # Assuming `pat_user` is the currently logged-in user
        pat_user = request.user if request.user.is_authenticated else None

        # Create a new Patient instance
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
            email=email,
            address=address,
            pat_user=pat_user
        )

        # Save the new patient to the database
        try:
            patient.save()
            messages.success(request, "Patient profile created successfully.")
            return redirect('patient_detail',pk=patient.pk )  # Redirect to patient list or desired URL
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    # If GET request, render the template with the form
    return render(request,'patient_create.html')


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)  # Retrieve the specific patient by primary key
    return render(request, 'patient_detail.html', {'patient': patient})


def doctor_home(request):
    # Fetch the doctor profile associated with the logged-in user
    doctor_profiles = Doctor.objects.filter(doctor_user=request.user)

    # Check if the logged-in user has an associated doctor profile
    doctor_profile = doctor_profiles.first() if doctor_profiles.exists() else None

    # Fetch upcoming appointments for the doctor
    if doctor_profile:
        # Update the filter to use the correct 'date' field instead of 'appointment_date'
        appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('date', 'shift')

    context = {
        'doctor': doctor_profile,
        'appointments': appointments,
    }
    return render(request, 'doctor_home.html', context)



def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, 'doctor_detail.html', {'doctor': doctor})




def create_doctor(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        specialization = request.POST.get('specialization')
        phone_number = request.POST.get('phone_number')
        experience = request.POST.get('experience')
        clinic_address = request.POST.get('clinic_address')
        image = request.FILES.get('image')
        
        doctor = Doctor.objects.create(
            doctor_user=request.user,
            first_name=first_name,
            last_name=last_name,
            specialization=specialization,
            phone_number=phone_number,
            experience=experience,
            clinic_address=clinic_address,
            image=image
        )
        return redirect('doctor_detail', pk=doctor.pk)  # Redirect to doctor detail page after creation
    
    return render(request, 'doctor_create.html')  # Render the creation template



def edit_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    if request.method == 'POST':
        # Update doctor fields
        doctor.first_name = request.POST.get('first_name')
        doctor.last_name = request.POST.get('last_name')
        doctor.specialization = request.POST.get('specialization')
        doctor.phone_number = request.POST.get('phone_number')
        doctor.experience = request.POST.get('experience')
        doctor.clinic_address = request.POST.get('clinic_address')

        # Update image if provided
        if request.FILES.get('image'):
            doctor.image = request.FILES.get('image')

        # Handle availability JSON field
        availability = request.POST.get('availability')
        if availability:  # Ensure it's not None
            try:
                doctor.availability = json.loads(availability)
            except json.JSONDecodeError:
                # Handle invalid JSON gracefully
                doctor.availability = {}
        else:
            # Set default value if not provided
            doctor.availability = {}

        # Save doctor instance
        doctor.save()
        return redirect('doctor_detail', pk=doctor.pk)

    return render(request, 'doctor_edit.html', {'doctor': doctor})




def schedule_create(request):
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        doctor_id = request.POST.get('doctor')
        shifts = request.POST.get('shifts')
        day = request.POST.get('day')

        doctor = Doctor.objects.get(id=doctor_id)

        # Validate and create a new Schedule
        if not Schedule.objects.filter(doctor=doctor, day=day, shifts=shifts, specialization=specialization).exists():
            schedule = Schedule(
                specialization=specialization,
                doctor=doctor,
                shifts=shifts,
                day=day
            )
            schedule.save()
            return redirect('schedule_list')
        else:
            return HttpResponse("Schedule for the selected doctor, day, and shift already exists.", status=400)

    # Passing choices and doctors to the template
    doctors = Doctor.objects.all()
    context = {
        'doctors': doctors,
        'doctors_json': json.dumps(
            [{'id': doctor.id, 'specialization': doctor.specialization, 'first_name': doctor.first_name}
             for doctor in doctors],
            cls=DjangoJSONEncoder
        ),
        'shift_choices': Schedule.SHIFTS,
        'day_choices': Schedule.DAYS_OF_WEEK,
    }
    return render(request, 'schedule_create.html', context)



def schedule_list(request):
    schedules = Schedule.objects.all()
    return render(request, 'schedule_list.html', {'schedules': schedules})





def create_appointment(request):
    if request.method == 'POST':
        # Retrieve form data
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        schedule_id = request.POST.get('schedule')

        # Validate input and fetch related objects
        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
        schedule = get_object_or_404(Schedule, id=schedule_id)

        # Check if an appointment already exists for the same patient, doctor, schedule, and date
        if Appointment.objects.filter(
            patient=patient, doctor=doctor, schedule=schedule, date=now().date()
        ).exists():
            # Provide error context
            return render(request, 'create_appointment.html', {
                'patients': Patient.objects.filter(pat_user__role=4),
                'doctors': Doctor.objects.filter(doctor_user__role=3),
                'schedules': Schedule.objects.all(),
                'error_message': 'This appointment already exists.',
            })

        # Create and save a new appointment
        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            schedule=schedule,
        )
        appointment.save()

        # Redirect to a confirmation page (update the URL name as needed)
        return redirect('appoinment_conform')

    # Handle AJAX request for fetching schedules
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        doctor_id = request.GET.get('doctor_id')
        schedules = Schedule.objects.filter(doctor_id=doctor_id).values('id', 'day', 'shifts')
        return JsonResponse({'schedules': list(schedules)})

    # Prepare context data for the GET request
    context = {
        'patients': Patient.objects.filter(pat_user__role=4),
        'doctors': Doctor.objects.filter(doctor_user__role=3),
    }
    return render(request, 'create_appointment.html', context)


def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointment_detail.html', {"appointment": appointment})





def list_appointments(request):
    doctor_profiles = Doctor.objects.filter(doctor_user=request.user)

    # Check if the logged-in user has an associated doctor profile
    doctor_profile = doctor_profiles.first() if doctor_profiles.exists() else None

    if request.user.role == 2:  # Assuming role '2' for doctors
        # Fetch only the appointments for the logged-in doctor
        appointments = Appointment.objects.filter(doctor=request.user).select_related('patient', 'doctor', 'schedule').order_by('schedule__shifts')
    else:
        # For other users (e.g., patients), fetch all appointments
        appointments = Appointment.objects.filter(doctor=doctor_profile).select_related('patient', 'doctor', 'schedule').order_by('schedule__shifts')

    # Group appointments by schedule
    grouped_appointments = []
    for schedule, group in groupby(appointments, key=attrgetter('schedule')):
        grouped_appointments.append((schedule, list(group)))

    context = {
        'appointments': appointments,
        'grouped_appointments': grouped_appointments,
        'patient': request.user.role == 4,  # Assuming '4' is the role for a patient
        'doctor': request.user.role == 2,  # Flag to check if the user is a doctor
    }
    return render(request, 'list_appointments.html', context)




def appoinment_conform(request):
    return render(request,'appoinment_conform.html')


def appointment_delete(request, pk):
    print(f"Attempting to delete appointment with pk={pk}")
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        print(f"Deleting appointment: {appointment}")
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
        return redirect('doctor_home')

    context = {
        'appointment': appointment,
    }

    return render(request, 'appointment_delete.html', context)


def add_recep(request,id):
    main = CustomUser.objects.get(id=id)
    context = {'main':main}
    return render(request,'add_recep.html',context)

def add_doctor(request,id):
    main = CustomUser.objects.get(id=id)
    context = {'main':main}
    return render(request,'add_doctor.html',context)

def add_patient(request,id):
    main = CustomUser.objects.get(id=id)
    context = {'main':main}
    return render(request,'add_patient.html',context)
    



def approve_user(request,id):
    main = CustomUser.objects.get(id=id)
    main.is_approved = True
    main.save()
    return redirect('admin_home')



def remove_user(request,id):
    main = CustomUser.objects.get(id=id)
    
    main.delete()
    return redirect('admin_home')






