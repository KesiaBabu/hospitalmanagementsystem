from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('loginpage',views.loginpage,name='loginpage'),
    path('signup_doctor',views.signup_doctor,name='signup_doctor'),
    path('signup_pharmacy',views.signup_pharmacy,name='signup_pharmacy'),
    path('reception_home',views.reception_home,name='reception_home'),
    path('loginfun',views.loginfun,name='loginfun'),
    path('logout',views.logout,name='logout'),
    path('dept',views.dept,name='dept'),
    path('add_dept',views.add_dept,name='add_dept'),
    path('show_dept',views.show_dept,name='show_dept'),
    path('delete_dept/<int:id>',views.delete_dept,name='delete_dept'),
    path('doc_reg',views.doc_reg,name='doc_reg'),
    path('doc_home',views.doc_home,name='doc_home'),
    path('register_patient',views.register_patient,name='register_patient'),
    path('appointment_form/<int:patient_id>',views.appointment_form,name='appointment_form'),
    # path('appointment_confirm/<int:patient_id>/<int:appointment_id>/', views.appointment_confirm, name='appointment_confirm'),
    path('appointment_list', views.appointment_list, name='appointment_list'),
    path('consultation_form/<int:appointment_id>', views.consultation_form, name='consultation_form'),
    path('submit_consultation/<int:appointment_id>', views.submit_consultation, name='submit_consultation'),
    path('search_patient',views.search_patient,name='search_patient'),
    path('change_password',views.change_password,name='change_password'),
    path('r_search_patient',views.r_search_patient,name='r_search_patient'),
    path('pha_reg',views.pha_reg,name='pha_reg'),
    path('pharmacy_home',views.pharmacy_home,name='pharmacy_home'),
    path('p_change_password',views.p_change_password,name='p_change_password'),
    path('p_search_patient',views.p_search_patient,name='p_search_patient'),
    path('pres_details',views.pres_details,name='pres_details'),
    path('appointment_details/<int:patient_id>',views.appointment_details,name='appointment_details'),
    path('book_appointment',views.book_appointment,name='book_appointment'),
    path('reassign_patient',views.reassign_patient,name='reassign_patient'),
    path('reassign_patient_success',views.reassign_patient_success,name='reassign_patient_success'),
    path('reassigned_details',views.reassigned_details,name='reassigned_details'),
    path('recent_prescriptions',views.recent_prescriptions,name='recent_prescriptions'),
    
    
]