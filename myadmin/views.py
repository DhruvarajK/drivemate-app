from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Q, Sum, Count, Avg

from .permissions import IsAdmin  # Assuming you have a mixin or decorator for admin check
from accounts.models import User, Driver
from vehicles.models import Vehicle, VehicleImage
from rides.models import Ride, Rating, Subscription, RidePurpose  # Assuming RidePurpose is in rides

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.session['user_role'] == 'admin'):
            messages.error(request, 'Access denied. Admin only.')
            return HttpResponseRedirect('/')  # Or login URL
        return super().dispatch(request, *args, **kwargs)

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        # Core stats (same as before)
        total_users = User.objects.count()
        total_drivers = Driver.objects.count()
        total_vehicles = Vehicle.objects.filter(active=True).count()
        total_rides = Ride.objects.count()
        total_completed_rides = Ride.objects.filter(status=Ride.Status.COMPLETED).count()
        total_revenue = Ride.objects.filter(status=Ride.Status.COMPLETED).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        avg_rating = Rating.objects.aggregate(avg=Avg('score'))['avg'] or 0.0
        pending_verifications_drivers = Driver.objects.filter(verified=False).count()
        pending_verifications_vehicles = Vehicle.objects.filter(verified=False).count()
        active_subscriptions = Subscription.objects.filter(active=True).count()
        recent_rides_count = Ride.objects.filter(start_time__date__gte=week_ago).count()
        revenue_today = Ride.objects.filter(
            status=Ride.Status.COMPLETED, end_time__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Advanced metrics
        top_drivers = Driver.objects.annotate(
            total_rides=Count('rides', filter=Q(rides__status=Ride.Status.COMPLETED)),
            avg_rating=Avg('received_ratings__score')
        ).filter(total_rides__gt=0).order_by('-total_rides')[:5]

        top_vehicles = Vehicle.objects.annotate(
            total_rides=Count('rides', filter=Q(rides__status=Ride.Status.COMPLETED)),
            avg_rating=Avg('ratings__score')
        ).filter(total_rides__gt=0).order_by('-total_rides')[:5]

        revenue_trend = [
            Ride.objects.filter(
                status=Ride.Status.COMPLETED, 
                end_time__date=(today - timedelta(days=i))
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            for i in range(7)
        ]

        context.update({
            'dashboard': {
                'total_users': total_users,
                'total_drivers': total_drivers,
                'total_vehicles': total_vehicles,
                'total_rides': total_rides,
                'total_completed_rides': total_completed_rides,
                'total_revenue': total_revenue,
                'avg_rating': round(avg_rating, 2),
                'pending_verifications_drivers': pending_verifications_drivers,
                'pending_verifications_vehicles': pending_verifications_vehicles,
                'active_subscriptions': active_subscriptions,
                'recent_rides_count': recent_rides_count,
                'revenue_today': revenue_today,
                'top_drivers': [
                    {'name': d.user.name, 'rides': d.total_rides, 'avg_rating': round(d.avg_rating or 0, 2)}
                    for d in top_drivers
                ],
                'top_vehicles': [
                    {'reg_num': v.registration_number, 'rides': v.total_rides, 'avg_rating': round(v.avg_rating or 0, 2)}
                    for v in top_vehicles
                ],
                'revenue_trend_last_7_days': revenue_trend,
            }
        })
        return context

class AdminRevenueView(AdminRequiredMixin, TemplateView):
    template_name = 'revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Ride.objects.filter(status=Ride.Status.COMPLETED)
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(end_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__date__lte=end_date)
        
        total_revenue = queryset.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        context['revenue'] = {
            'total_revenue': total_revenue,
            'currency': 'INR',
            'rides_count': queryset.count(),
            'avg_fare': queryset.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
        }
        return context

class AdminRidesListView(AdminRequiredMixin, ListView):
    model = Ride
    template_name = 'rides_list.html'
    context_object_name = 'rides'
    paginate_by = 20

    def get_queryset(self):
        queryset = Ride.objects.select_related('customer', 'driver__user', 'vehicle', 'purpose').all()
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        
        customer_id = self.request.GET.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        driver_id = self.request.GET.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        return queryset.order_by('-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For status choices in filter
        context['ride_status_choices'] = Ride.Status.choices
        return context

class AdminUserManagementView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'users_management.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        users = User.objects.annotate(
            avg_rating=Avg('driver_profile__received_ratings__score'),
            total_ratings=Count('driver_profile__received_ratings')
        ).select_related('driver_profile')
        role_filter = self.request.GET.get('role')
        if role_filter:
            users = users.filter(role=role_filter)
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Enhance with ratings data
        for user in context['users']:
            if hasattr(user, 'driver_profile') and user.driver_profile:
                ratings = Rating.objects.filter(driver=user.driver_profile).aggregate(
                    avg_score=Avg('score'), total=Count('id')
                )
                user.avg_rating = ratings['avg_score'] or 0
                user.total_ratings = ratings['total'] or 0
                user.recent_feedback = [
                    {'score': r.score, 'feedback': r.feedback[:100] + '...' if r.feedback else None}
                    for r in Rating.objects.filter(driver=user.driver_profile).order_by('-created_at')[:3]
                ]
            else:
                user.avg_rating = 0
                user.total_ratings = 0
                user.recent_feedback = []
        
        context['user_role_choices'] = User.ROLE_CHOICES
        return context

class AdminVehiclesManagementView(AdminRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles_management.html'
    context_object_name = 'vehicles'
    paginate_by = 20

    def get_queryset(self):
        queryset = Vehicle.objects.select_related('owner', 'current_driver__user').prefetch_related('images').all()
        owner_id = self.request.GET.get('owner_id')
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        verified_filter = self.request.GET.get('verified')
        if verified_filter is not None:
            verified = verified_filter.lower() == 'true'
            queryset = queryset.filter(verified=verified)
        return queryset.order_by('-created_at')

class AdminDriverVerificationListView(AdminRequiredMixin, ListView):
    model = Driver
    template_name = 'driver_verifications_list.html'
    context_object_name = 'drivers'
    paginate_by = 20

    def get_queryset(self):
        return Driver.objects.select_related('user').filter(verified=False).order_by('-user__created_at')

class AdminDriverVerificationDetailView(AdminRequiredMixin, DetailView):
    model = Driver
    template_name = 'driver_verification_detail.html'
    context_object_name = 'driver'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Driver.objects.select_related('user')

    def post(self, request, *args, **kwargs):
        driver = self.get_object()
        action = request.POST.get('action')
        if action == 'verify':
            driver.verified = True
            driver.background_check_passed = True
            driver.save(update_fields=['verified', 'background_check_passed'])
            messages.success(request, f'Driver {driver.user.name} verified successfully.')
        elif action == 'reject':
            driver.verified = False
            driver.background_check_passed = False
            driver.save(update_fields=['verified', 'background_check_passed'])
            messages.error(request, f'Driver {driver.user.name} verification rejected.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('admin-driver-verification-detail', kwargs={'pk': self.object.pk})

class AdminVehicleVerificationListView(AdminRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicle_verifications_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20

    def get_queryset(self):
        return Vehicle.objects.select_related('owner').prefetch_related('images').filter(verified=False).order_by('-created_at')



class AdminVehicleVerificationDetailView(AdminRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'vehicle_verification_detail.html'
    context_object_name = 'vehicle'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Vehicle.objects.select_related('owner', 'current_driver__user').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_images'] = self.object.images.all() if self.object else []
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() 
        vehicle = self.object

        action = request.POST.get('action')

        if action == 'approve':
            vehicle.verified = True
            vehicle.active = True
            vehicle.save(update_fields=['verified', 'active'])
            messages.success(request, f'Vehicle {vehicle.registration_number} approved successfully.')
        elif action == 'reject':
            vehicle.verified = False
            vehicle.active = False
            vehicle.save(update_fields=['verified', 'active'])
            messages.error(request, f'Vehicle {vehicle.registration_number} rejected.')

        return redirect('admin-vehicle-verification-detail', pk=vehicle.pk)


def admin_driver_verify(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    driver.verified = True
    driver.background_check_passed = True
    driver.save(update_fields=['verified', 'background_check_passed'])
    messages.success(request, f'Driver {driver.user.name} verified successfully.')
    return redirect('admin-driver-verification-detail', pk=pk)

def admin_driver_reject(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    driver.verified = False
    driver.background_check_passed = False
    driver.save(update_fields=['verified', 'background_check_passed'])
    messages.error(request, f'Driver {driver.user.name} verification rejected.')
    return redirect('admin-driver-verification-detail', pk=pk)

def admin_vehicle_approve(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.verified = True
    vehicle.active = True
    vehicle.save(update_fields=['verified', 'active'])
    messages.success(request, f'Vehicle {vehicle.registration_number} approved successfully.')
    return redirect('admin-vehicle-verification-detail', pk=pk)

def admin_vehicle_reject(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.verified = False
    vehicle.active = False
    vehicle.save(update_fields=['verified', 'active'])
    messages.error(request, f'Vehicle {vehicle.registration_number} approval rejected.')
    return redirect('admin-vehicle-verification-detail', pk=pk)