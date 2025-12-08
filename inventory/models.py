from django.db import models

# Create your models here.
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
    # Link to the client who made the order
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    # Link to the bag being purchased
    bag = models.ForeignKey(FinishedBag, on_delete=models.CASCADE, related_name='sales')
    # How many bales they are buying
    quantity_ordered = models.PositiveIntegerField(verbose_name="Quantity (Bales)")
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client.name} ({self.quantity_ordered} bales)"

    def total_cost_placeholder(self):
        # In the future, you could multiply quantity * price here
        return "TBD"