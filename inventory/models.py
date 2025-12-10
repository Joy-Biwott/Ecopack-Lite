from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- EXISTING MODELS ---
class FinishedBag(models.Model):
    VARIETY_CHOICES = [
        ('#15', '#15 Small'),
        ('#22', '#22 Medium'),
        ('#25', '#25 Large'),
        ('7X12', '7X12 White'),
        ('9X15', '9X15 White'),
    ]

    COLOR_CHOICES = [
        ('White', 'White'),
        ('Red', 'Red'),
        ('Green', 'Green'),
        ('Blue', 'Blue'),
    ]

    GSM_CHOICES = [
        (40, '40 GSM'),
        (60, '60 GSM'),
        (80, '80 GSM'),
        (100, '100 GSM'),
    ]

    variety = models.CharField(max_length=20, choices=VARIETY_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    gsm = models.IntegerField(choices=GSM_CHOICES, verbose_name='GSM Thickness')
    quantity_bales = models.IntegerField(default=0, verbose_name="Stock Quantity (Bales)")
    location = models.CharField(max_length=100, default="Athiriver Warehouse")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.variety} - {self.color} ({self.gsm} GSM)"


class Client(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    bag = models.ForeignKey(FinishedBag, on_delete=models.CASCADE, related_name='sales')
    quantity_ordered = models.PositiveIntegerField(verbose_name="Quantity (Bales)")
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client.name} ({self.quantity_ordered} bales)"

    def total_cost_placeholder(self):
        return "TBD"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField(help_text="Describe your idea or issue here...")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.user.username}"


# --- NEW: PROFILE MODEL (Security Module) ---
class Profile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager','Manager'),
        ('Staff', 'Staff'),
    ]
    # Link to the built-in User model (One-to-One)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Staff')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# --- AUTOMATION SIGNALS ---
# These functions automatically create a Profile whenever a new User is created.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()