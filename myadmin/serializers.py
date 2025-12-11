from rest_framework import serializers
from decimal import Decimal
from accounts.models import User, Driver
from vehicles.models import Vehicle, VehicleImage
from rides.models import Ride, Rating, RideRequest, Subscription
from django.db.models import Sum, Count, Avg
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'gender', 'role', 'language_preference', 'is_active', 'created_at', 'updated_at']

class DriverVerificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'user_id', 'license_number', 'license_expiry', 'experience_years', 
                  'verified', 'background_check_passed', 'rating', 'is_available', 'profile_pic', 'id_proof']
        read_only_fields = ['id', 'user', 'rating', 'is_available']  # is_available can be managed separately

    def validate_license_expiry(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("License expiry date cannot be in the past.")
        return value

class VehicleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    current_driver = UserSerializer(source='current_driver.user', read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ['id', 'owner', 'current_driver', 'vehicle_type', 'make', 'model', 'year', 'color', 
                  'registration_number', 'seat_capacity', 'ac', 'transmission', 'fuel_type', 
                  'fitness_cert_expiry', 'insurance_expiry', 'permit_expiry', 'per_km_rate', 
                  'per_min_rate', 'verified', 'active', 'created_at', 'updated_at', 'images']

    def get_images(self, obj):
        return [VehicleImageSerializer(img).data for img in obj.images.all()]

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'caption', 'is_primary', 'uploaded_at']

class VehicleVerificationSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner', write_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'owner_id', 'vehicle_type', 'make', 'model', 'year', 'color', 
                  'registration_number', 'seat_capacity', 'ac', 'transmission', 'fuel_type', 
                  'fitness_cert_expiry', 'insurance_expiry', 'permit_expiry', 'per_km_rate', 
                  'per_min_rate', 'verified', 'active']
        read_only_fields = ['id']

    def validate_fitness_cert_expiry(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Fitness certificate expiry cannot be in the past.")
        return value

    def validate_insurance_expiry(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Insurance expiry cannot be in the past.")
        return value

    def validate_permit_expiry(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Permit expiry cannot be in the past.")
        return value

class RideSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    driver = UserSerializer(source='driver.user', read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    purpose = serializers.CharField(source='purpose.name', read_only=True)

    class Meta:
        model = Ride
        fields = ['id', 'customer', 'driver', 'vehicle', 'ride_mode', 'start_location', 'start_latitude', 
                  'start_longitude', 'end_location', 'end_latitude', 'end_longitude', 'start_time', 
                  'end_time', 'status', 'female_driver_preference', 'purpose', 'actual_distance_km', 
                  'actual_duration_min', 'base_fare', 'tax_amount', 'discount_amount', 'total_amount', 
                  'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'driver', 'vehicle', 'purpose', 'base_fare', 'tax_amount', 
                            'total_amount', 'created_at', 'updated_at']

class RideRequestSerializer(serializers.ModelSerializer):
    ride = RideSerializer(read_only=True)
    driver = UserSerializer(source='driver.user', read_only=True)

    class Meta:
        model = RideRequest
        fields = ['id', 'ride', 'driver', 'status', 'requested_at', 'responded_at']
        read_only_fields = ['id', 'requested_at']

class RatingSerializer(serializers.ModelSerializer):
    ride = RideSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    driver = UserSerializer(source='driver.user', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'ride', 'customer', 'driver', 'vehicle', 'score', 'feedback', 'created_at']
        read_only_fields = ['id', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    plan = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'customer', 'plan', 'driver', 'vehicle', 'start_date', 'end_date', 'active']
        read_only_fields = ['id']

class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_drivers = serializers.IntegerField()
    total_vehicles = serializers.IntegerField()
    total_rides = serializers.IntegerField()
    total_completed_rides = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_rating = serializers.FloatField()
    pending_verifications_drivers = serializers.IntegerField()
    pending_verifications_vehicles = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    recent_rides_count = serializers.IntegerField()  # Last 7 days
    revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)