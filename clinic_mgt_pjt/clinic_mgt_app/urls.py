from django.urls import path
from .import views

urlpatterns =[
    path('register', views.register, name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('',views.not_login,name='not_login'),

    path('add_recep/<int:id>/',views.add_recep,name='add_recep'),
    path('add_doctor/<int:id>/',views.add_doctor,name='add_doctor'),
    path('add_patient/<int:id>/',views.add_patient,name='add_patient'),


    path('approve/<int:id>/',views.approve_user,name='approve'),
    path('remove/<int:id>/',views.remove_user,name='remove'),


    path('admin_home/',views.admin_home,name='admin_home'),

    path('doctor_list/',views.doctor_list,name='doctor_list'),
    path('delete_doctor/',views.delete_doctor,name='delete_doctor'),

    path('patient_list/',views.patient_list,name='patient_list'),
    path('delete_patient/',views.delete_patient,name='delete_patient'),

    path('receptionist_list/', views.receptionist_list, name='receptionist_list'),
    path('delete_receptionist/', views.delete_receptionist, name='delete_receptionist'),



    path('patient_home/',views.patient_home,name='patient_home'),
    path('patient_create/',views.patient_create,name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),

    path('recep_home',views.recep_home,name='recep_home'),
    path("create_receptionist_profile/", views.create_receptionist_profile, name="create_receptionist_profile"),
    path('receptionist/<int:pk>/', views.receptionist_profile_detail, name='receptionist_profile_detail'),
    path('receptionist/edit/<int:pk>/', views.edit_receptionist_profile, name='edit_receptionist_profile'),


    path('doctor_home/',views.doctor_home,name='doctor_home'),
    path('create_doctor/',views.create_doctor,name='create_doctor'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/edit/<int:pk>/', views.edit_doctor, name='doctor_edit'),

    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/list/', views.schedule_list, name='schedule_list'),


    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('list_appointments/',views.list_appointments,name='list_appointments'),
    path('appoinment_conform/',views.appoinment_conform,name='appoinment_conform'),
    path('delete/<int:pk>/',views.appointment_delete, name='appointment_delete'),

    path('prescription/create/<int:appointment_id>/', views.create_prescription, name='create_prescription'),
    path('prescription/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    path('medicine/create/', views.create_medicine, name='create_medicine'),
    path('medicine/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('medicine/<int:medicine_id>/create_dose/', views.create_dose, name='create_dose'),
    path('test/create/', views.create_test, name='create_test'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),


    path('forgotpassword/',views.forgot_password,name='forgot_password'),
    path('verfy_otp/<int:id>/',views.otp_verify,name='otp_verify'),
    path('passwordreset/<int:id>/',views.password_reset,name='password_reset'),
    

]