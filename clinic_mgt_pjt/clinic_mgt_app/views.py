from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from datetime import datetime
import json
from django.db.models import Q
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
import random
from django.core.mail import send_mail
    



def register(request):
    # Filter role choices based on the logged-in user's role
    if request.user.role == 1:  # Admin
        filter_ROLE_CHOICE = [(id, name) for id, name in ROLE_CHOICE if name in ['Receptionist', 'Doctor','Pharmacist']]
    elif request.user.role == 2:  # Receptionist
        filter_ROLE_CHOICE = [(id, name) for id, name in ROLE_CHOICE if name == 'Patient']
    else:
        return HttpResponse("You do not have permission to register users.")

    if request.method == 'POST':
        username = request.POST.get('Name')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        role = int(request.POST.get('role'))

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
                elif user.role == 5:
                    if Pharmacistprofile.objects.filter(phar_user=user).exists():
                        return redirect('pharmacist_home')
                    else:
                        return redirect('Pharmacist_create')
                    
                    

                    
    
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def not_login(request):
    return render(request,'not_login.html')



def admin_home(request):
    all_users = CustomUser.objects.all()
    receptionists = all_users.filter(role=2, is_approved=False)
    doctors = all_users.filter(role=3, is_approved=False)
    patients = all_users.filter(role=4, is_approved=False)
    pharmacists = all_users.filter(role=5, is_approved=False)  # Assuming role=5 for pharmacists
    total_receptionists = all_users.filter(role=2).count()
    total_doctors = all_users.filter(role=3).count()
    total_patients = all_users.filter(role=4).count()
    total_pharmacists = all_users.filter(role=5).count()  # Total pharmacists
    total_appointments = Appointment.objects.count()
    pending_approvals = all_users.filter(is_approved=False).count()

    context = {
        'receptionists': receptionists,
        'doctors': doctors,
        'patients': patients,
        'pharmacists': pharmacists,  # Add pharmacists to the context
        'total_receptionists': total_receptionists,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_pharmacists': total_pharmacists,  # Pass total pharmacists
        'total_appointments': total_appointments,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'admin_home.html', context)



def admin_profile_detail(request):
    admin_user = get_object_or_404(CustomUser, id=request.user.id)
    return render(request, 'admin_profile_detail.html', {'admin_user': admin_user})



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
    

def pharmacist_list(request):
    pharmacists = Pharmacistprofile.objects.all()
    context = {'pharmacists': pharmacists}

    return render(request,'pharmacist_list.html',context)


def delete_pharmacist(request):
    if request.method == "POST":
        pharmacist_id = request.POST.get('pharmacist_id')
        pharmacist = get_object_or_404(Pharmacistprofile, id=pharmacist_id)
        pharmacist.delete()
        return redirect('pharmacist_list')
   





def recep_home(request):
    
    doctors = Doctor.objects.all()
    schedules = Schedule.objects.all()
    medicines = Medicine.objects.all()
    
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

    
    context = {
        'receptionist_profile': receptionist_profile,
        'doctors': doctors,
        'schedules': schedules,
        'medicines': medicines
        
    }

    return render(request, 'recep_home.html', context)




def create_receptionist_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        clinic_name = request.POST.get('clinic_name')
        emergency_contact = request.POST.get('emergency_contact')

        
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


from django.shortcuts import render, get_object_or_404
from .models import Pharmacistprofile

def pharmacist_home(request):
    # Assuming there is a one-to-one relationship between the user and Pharmacistprofile
    pharmacist = Pharmacistprofile.objects.filter(phar_user=request.user).first()  # Replace with your relationship logic
    return render(request, 'pharmacist_home.html', {'pharmacist': pharmacist})







def Pharmacist_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address', '')
        pharmacy_name = request.POST.get('pharmacy_name')
        emergency_contact = request.POST.get('emergency_contact', '')

        # Assuming `request.user` is linked to a `CustomUser`
        pharmacist_profile = Pharmacistprofile.objects.create(
            phar_user=request.user,
            name=name,
            contact_number=contact_number,
            address=address,
            pharmacy_name=pharmacy_name,
            emergency_contact=emergency_contact
        )
        return redirect('pharmacist_home')  

    return render(request, 'Pharmacist_create.html')



def pharmacist_detail(request, pk):
    pharmacist = get_object_or_404(Pharmacistprofile, pk=pk)
    return render(request, 'pharmacist_profile.html', {'pharmacist': pharmacist})






def patient_home(request):
    # Retrieve the logged-in patient's profile
    patient = Patient.objects.filter(pat_user=request.user).first()

    if not patient:
        return render(request, 'patient_profile_missing.html')
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'schedule')

    doctors = Doctor.objects.all()
    schedules = Schedule.objects.filter(doctor__in=doctors)

    
    context = {
        'patient': patient,
        'doctors': doctors,
        'schedules': schedules,
        'appointments': appointments,
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
        shifts_list = request.POST.getlist('shifts[]')
        days_list = request.POST.getlist('day[]')

        doctor = Doctor.objects.get(id=doctor_id)

        # Iterate through shifts and days to create schedules
        for shifts, day in zip(shifts_list, days_list):
            if not Schedule.objects.filter(doctor=doctor, day=day, shifts=shifts, specialization=specialization).exists():
                schedule = Schedule(
                    specialization=specialization,
                    doctor=doctor,
                    shifts=shifts,
                    day=day
                )
                schedule.save()
            else:
                return HttpResponse(
                    f"Schedule for {shifts} shift on {day} for the selected doctor already exists.",
                    status=400
                )

        return redirect('schedule_list')

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
    query = request.GET.get('query', '').strip().lower()  # Single input field for all queries

    # Initialize queryset
    schedules = Schedule.objects.all()

    if query:
        # Apply filters: search across doctor name, specialization, and day
        schedules = schedules.filter(
            Q(doctor__first_name__icontains=query) |
            Q(doctor__specialization__icontains=query) |
            Q(day__icontains=query)  # Adjust as needed for your `day` field
        )

    context = {
        'schedules': schedules,
        'query': query,
    }
    return render(request, 'schedule_list.html', context)









def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)

    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        doctor_id = request.POST.get('doctor')
        shifts = request.POST.get('shifts')
        day = request.POST.get('day')

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Update the schedule object
        schedule.specialization = specialization
        schedule.doctor = doctor
        schedule.shifts = shifts
        schedule.day = day
        schedule.save()

        return redirect('schedule_list')

    # Pass the schedule object to the template for editing
    doctors = Doctor.objects.all()
    context = {
        'schedule': schedule,
        'doctors': doctors,
        'shift_choices': Schedule.SHIFTS,
        'day_choices': Schedule.DAYS_OF_WEEK,
    }
    return render(request, 'schedule_edit.html', context)


def delete_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    if request.user.is_authenticated:  
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")  

    return redirect('schedule_list')  





def create_appointment(request):
    if request.method == 'POST':
        # Retrieve form data
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        schedule_id = request.POST.get('schedule')
        appointment_date = request.POST.get('date')

        # Validate input and fetch related objects
        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
        schedule = get_object_or_404(Schedule, id=schedule_id)

        # Convert date string to a datetime object
        try:
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'create_appointment.html', {
                'patients': Patient.objects.filter(pat_user__role=4),
                'doctors': Doctor.objects.filter(doctor_user__role=3),
                'schedules': Schedule.objects.all(),
                'error_message': 'Invalid date format. Please use YYYY-MM-DD.',
            })

        # Check if an appointment already exists for the same patient, doctor, schedule, and date
        if Appointment.objects.filter(
            patient=patient, doctor=doctor, schedule=schedule, date=appointment_date
        ).exists():
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
            date=appointment_date
        )
        appointment.save()

        return redirect('appoinment_conform')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        doctor_id = request.GET.get('doctor_id')
        schedules = Schedule.objects.filter(doctor_id=doctor_id).values('id', 'day', 'shifts')
        return JsonResponse({'schedules': list(schedules)})

    context = {
        'patients': Patient.objects.filter(pat_user__role=4),
        'doctors': Doctor.objects.filter(doctor_user__role=3),
    }
    return render(request, 'create_appointment.html', context)



def appointment_detail(request, pk):
    # Get the appointment instance
    appointment = get_object_or_404(Appointment, pk=pk)

    # Fetch the related patient
    patient = appointment.patient

    # Check if the logged-in user is a doctor
    doctor = Doctor.objects.filter(doctor_user=request.user).first()

    # Fetch the prescription related to the appointment
    prescription = Prescription.objects.filter(appointment=appointment).first()

    # Prepare data for medicines and tests
    medicines = PrescriptionMedicine.objects.filter(prescription=prescription) if prescription else []
    tests = PrescriptionTest.objects.filter(prescription=prescription) if prescription else []

    # Calculate the total cost for medicines and tests
    total_medicine_cost = sum(medicine.medicine.dose_set.first().cost for medicine in medicines)
    total_test_cost = sum(test.test.cost for test in tests)

    # Calculate the total cost
    total_cost = total_medicine_cost + total_test_cost

    # Context for the template
    context = {
        'appointment': appointment,
        'patient': patient,
        'doctor': doctor,
        'prescription': prescription,
        'medicines': medicines,
        'tests': tests,
        'total_medicine_cost': total_medicine_cost,
        'total_test_cost': total_test_cost,
        'total_cost': total_cost,
    }

    return render(request, 'appointment_detail.html', context)



def patient_appointments(request, pk):
    # Get the patient using the provided primary key
    patient = get_object_or_404(Patient, pk=pk)

    # Check if the logged-in user is a doctor
    doctor = Doctor.objects.filter(doctor_user=request.user).first()

    # Fetch all appointments for the patient, filtering by doctor if the user is a doctor
    appointments = Appointment.objects.filter(patient=patient)

    if doctor:
        # If the logged-in user is a doctor, filter appointments by doctor
        appointments = appointments.filter(doctor=doctor)

    # Order appointments by date (most recent first)
    appointments = appointments.order_by('-date')

    # Context for the template
    context = {
        'patient': patient,
        'appointments': appointments,
    }

    return render(request, 'patient_appointments.html', context)











def list_appointments(request):
    doctor_profiles = Doctor.objects.filter(doctor_user=request.user)

    # Check if the logged-in user has an associated doctor profile
    doctor_profile = doctor_profiles.first() if doctor_profiles.exists() else None

    if request.user.role == 2:  # Assuming role '2' for doctors
        # Fetch only the appointments for the logged-in doctor
        appointments = Appointment.objects.filter(doctor=request.user).select_related('patient', 'doctor', 'schedule').order_by('schedule__shifts','id')
    else:
        # For other users (e.g., patients), fetch all appointments
        appointments = Appointment.objects.filter(doctor=doctor_profile).select_related('patient', 'doctor', 'schedule').order_by('schedule__shifts','id')

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





def create_prescription(request, appointment_id):
    medicines = Medicine.objects.all()
    doses = Dose.objects.all()
    tests = Test.objects.all()
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure the prescription is initialized for the appointment
    prescription, created = Prescription.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'final_submit':
            illness_description = request.POST.get('illness_description')
            date = request.POST.get('date')

            if not illness_description or not date:
                messages.error(request, "Illness description and date are required.")
                return redirect('create_prescription', appointment_id=appointment_id)

            prescription.illness_description = illness_description
            prescription.date = date
            prescription.save()
            messages.success(request, "Prescription finalized successfully!")
            return redirect('create_prescription', appointment_id=appointment_id)

        elif action == 'add_medicine':
            medicine_ids = request.POST.getlist('medicine_id[]')
            per_day = request.POST.getlist('per_day[]')
            duration_days = request.POST.getlist('duration_days[]')

            if not medicine_ids:
                messages.error(request, "Please add at least one medicine.")
                return redirect('create_prescription', appointment_id=appointment_id)

            for i in range(len(medicine_ids)):
                medicine = get_object_or_404(Medicine, id=medicine_ids[i])
                PrescriptionMedicine.objects.create(
                    prescription=prescription,
                    medicine=medicine,
                    per_day=per_day[i],
                    duration_days=duration_days[i]
                )
            messages.success(request, "Medicines added successfully!")
            return redirect('create_prescription', appointment_id=appointment_id)

        elif action == 'add_test':
            test_ids = request.POST.getlist('test_id[]')

            if not test_ids:
                messages.error(request, "Please add at least one test.")
                return redirect('create_prescription', appointment_id=appointment_id)

            for test_id in test_ids:
                test = get_object_or_404(Test, id=test_id)
                PrescriptionTest.objects.create(
                    prescription=prescription,
                    test=test
                )
            messages.success(request, "Tests added successfully!")
            return redirect('create_prescription', appointment_id=appointment_id)

    context = {
        'appointment': appointment,
        'medicines': medicines,
        'doses': doses,
        'tests': tests,
        'prescription': prescription,
    }
    return render(request, 'create_prescription.html', context)






def prescription_detail(request, prescription_id):
    # Fetch the current prescription and related details
    prescription = get_object_or_404(
        Prescription.objects.select_related('patient', 'doctor', 'appointment'),
        id=prescription_id
    )
    medicines = PrescriptionMedicine.objects.filter(prescription=prescription)
    tests = PrescriptionTest.objects.filter(prescription=prescription)

    # Fetch previous prescriptions for the same patient and doctor
    previous_prescriptions = Prescription.objects.filter(
        patient=prescription.patient,
        doctor=prescription.doctor
    ).exclude(id=prescription.id).filter(date__lt=prescription.date).order_by('-date')

    context = {
        'prescription': prescription,
        'medicines': medicines,
        'tests': tests,
        'previous_prescriptions': previous_prescriptions,  # Pass previous prescriptions to template
    }

    return render(request, 'prescription_detail.html', context)









def create_medicine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Medicine.objects.create(name=name)
            return redirect('pharmacist_home')  # Redirect to a medicine list or any relevant page
    return render(request, 'create_medicine.html')


def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'medicine_list.html', {'medicines': medicines})







def create_dose_medicin(request):
    # Fetch all medicines from the database
    medicines = Medicine.objects.all()
    

    if request.method == 'POST':
        # Get the selected medicine id
        medicine_id = request.POST.get('medicine')
        
        # You can now use this ID for whatever you need (e.g., create a dose)
        medicine = Medicine.objects.get(id=medicine_id)

        # Logic for creating a dose or other functionality can go here
        # For example:
        # Dose.objects.create(medicine=medicine, dose=dose_value, cost=cost_value)
        
        return redirect('medicine_detail', medicine_id=medicine.id)  # Redirect after successful action

    return render(request, 'create_dose_medicin.html', {'medicines': medicines})



def medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    doses = Dose.objects.filter(medicine=medicine)
    return render(request, 'medicine_detail.html', {'medicine': medicine, 'doses': doses})


def create_dose(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        dose = request.POST.get('dose')
        cost = request.POST.get('cost')

        Dose.objects.create(medicine=medicine, dose=dose, cost=cost)
        return redirect('medicine_detail', medicine_id=medicine.id)

    return render(request, 'create_dose.html', {'medicine': medicine})


def create_test(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')
        test = Test.objects.create(name=name, cost=cost)
        return redirect('test_detail', test_id=test.id)

    return render(request, 'create_test.html')


def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    return render(request, 'test_detail.html', {'test': test})



def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = CustomUser.objects.filter(username=username).first()
        if user:
            email = user.email
            otp = random.randrange(1000,9999)
            subject = 'Password Reset'
            message = f'Here is your otp - {otp}'
            from_email = 'junaidabdrahiman15@gmail.com'
            to = [email]
            send_mail(
                subject = subject,
                message = message,
                from_email =from_email,
                recipient_list = to,
                fail_silently = False
            )
            UserOTP.objects.update_or_create(
            user=user,
            defaults = {'otp':otp}
            )
            return redirect('otp_verify',user.id)
           
    return render(request,'forgot_password.html')




def otp_verify(request,id):
    user = CustomUser.objects.get(id=id)
    if request.method == 'POST':
        submitted_otp = request.POST.get('otp')
        user_otp_obj = UserOTP.objects.filter(user=user).first()
        send_otp = user_otp_obj.otp
        if submitted_otp == send_otp:
            messages.success(request, 'OTP Verified')
            return redirect('password_reset',user.id)
        messages.error(request, 'Please enter valid OTP')
        return redirect('otp_verify',id)
    
    return render(request,'otp_verify.html',context={'email':user.email})




def password_reset(request,id):
    user = CustomUser.objects.get(id=id)
    if request.method == "POST":
        password1=request.POST.get('password1') 
        password2=request.POST.get('password2')
        if password2 == password1:
            user.set_password(password2)
            user.save()
            return redirect('login') 
        
    return render(request,"password_reset.html")   





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
    



def approve_user(request, id):
    try:
        main = CustomUser.objects.get(id=id)
        main.is_approved = True
        main.save()
        return redirect('admin_home')
    except CustomUser.DoesNotExist:
        # Handle the case where the user does not exist
        return redirect('admin_home')

def remove_user(request, id):
    try:
        main = CustomUser.objects.get(id=id)
        main.delete()
        return redirect('admin_home')
    except CustomUser.DoesNotExist:
        # Handle the case where the user does not exist
        return redirect('admin_home')




def payment_page(request):
    # Example: Retrieve patient information from the database
    patients = Patient.objects.all()  # Replace `Patient` with your actual model name

    return render(request, 'payment.html', {'patients': patients})

def process_payment(request):
    if request.method == 'POST':
        # Perform payment processing logic here

        # Redirect back to the payment page with a success message
        return render(request, 'payment_success.html', {'payment_success': True, 'patients': Patient.objects.all()})

    return redirect('payment_page')  # Replace with the correct name of your payment page view
    





