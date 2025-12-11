from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from accounts.views import *
from rides.views import *
from payments.views import *
from myadmin.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health',health_check),
    path('', index,name='index'),
    path('model/', model,name='index'),
    path("register/customer/", customer_register, name="customer_register"),
    path("register/driver/", driver_register, name="driver_register"),
    
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("terms/", terms, name="terms"),

    path("dashboard/customer/", customer_dashboard, name="customer_dashboard"),
    path("dashboard/driver/", driver_dashboard, name="driver_dashboard"),
    
    path("customer/profile/", customer_profile_view, name="customer_profile"),
    path("customer/profile/edit/", customer_profile_edit, name="customer_profile_edit"),

    # Driver profile routes
    path("driver/profile/", driver_profile_view, name="driver_profile"),
    path("driver/profile/edit/", driver_profile_edit, name="driver_profile_edit"),
    path('create/', create_ride, name='create_ride'),
    path('select-driver/<int:ride_id>/', select_driver, name='select_driver'),
    path('driver/<int:driver_id>/', get_driver_details, name='get_driver_details'),
    
    path('my-trips/', my_trips, name='my_trips'),
    path('trip/<int:ride_id>/', trip_detail, name='trip_detail'),
    
    path("driver/requests/", driver_requests_list, name="driver_requests_list"),
    path("driver/requests/<int:pk>/", driver_request_detail, name="driver_request_detail"),
    path("driver/requests/<int:pk>/accept/", accept_ride_request, name="accept_ride_request"),
    path("ride-request/<int:pk>/distance/", ride_request_distance, name="ride_request_distance"),
    
    path('ride-requests/<int:pk>/set_ongoing/', set_ride_request_ongoing, name='set_ride_request_ongoing'),
    path('ride-requests/<int:pk>/end_ride/', end_ride_request, name='end_ride_request'),
    
    
    path('rides/<int:ride_id>/pay/', payment_page, name='ride_payment'),
    path('payments/create/', create_transaction, name='create_transaction'),
    path('payments/finalize/', finalize_transaction, name='finalize_transaction'),
    
    
    path('rate-ride/<int:ride_id>/', rate_ride, name='rate_ride'),
    path('view-driver-rating/<int:driver_id>/', view_driver_rating, name='view_driver_rating'),
    
    path('customer/payment-history/', customer_payment_history, name='customer_payment_history'),
    path('driver/payment-history/', driver_payment_history, name='driver_payment_history'),
    
    path("api/driver/toggle-availability/", api_toggle_driver_availability, name="api_toggle_availability"),
    
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('revenue/', AdminRevenueView.as_view(), name='admin-revenue'),
    path('rides/', AdminRidesListView.as_view(), name='admin-rides-list'),
    path('users-management/', AdminUserManagementView.as_view(), name='admin-users-management'),
    path('vehicles-management/', AdminVehiclesManagementView.as_view(), name='admin-vehicles-management'),
    path('driver-verifications/', AdminDriverVerificationListView.as_view(), name='admin-driver-verifications'),
    path('driver-verifications/<int:pk>/', AdminDriverVerificationDetailView.as_view(), name='admin-driver-verification-detail'),
    path('vehicle-verifications/', AdminVehicleVerificationListView.as_view(), name='admin-vehicle-verifications'),
    
    
    path('driver-verifications/<int:pk>/', AdminDriverVerificationDetailView.as_view(), name='admin-driver-verification-detail'),
    path('driver-verifications/<int:pk>/verify/', admin_driver_verify, name='admin-driver-verify'),
    path('driver-verifications/<int:pk>/reject/', admin_driver_reject, name='admin-driver-reject'),
    path('vehicle-verifications/<int:pk>/', AdminVehicleVerificationDetailView.as_view(), name='admin-vehicle-verification-detail'),
    path('vehicle-verifications/<int:pk>/approve/', admin_vehicle_approve, name='admin-vehicle-approve'),
    path('vehicle-verifications/<int:pk>/reject/', admin_vehicle_reject, name='admin-vehicle-reject'),

]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
