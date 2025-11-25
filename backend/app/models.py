from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ---------------- Profile ----------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username


# ---------------- Item ----------------
class Item(models.Model):
    CONDITION_CHOICES = [
        ('Available', 'Available'),
        ('Borrowed', 'Borrowed'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Lost', 'Lost')
    ]
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50, unique=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Available')
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.serial_number}) - Stock: {self.stock}"


# ---------------- BorrowTransaction ----------------
class BorrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    borrow_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.status})"

    def is_overdue(self):
        return (
            self.due_date is not None and
            self.status in ['Borrowed', 'Approved'] and
            timezone.now().date() > self.due_date
        )



# ---------------- Penalty ----------------
class Penalty(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]

    borrow_transaction = models.OneToOneField(BorrowTransaction, on_delete=models.CASCADE, related_name='penalty')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.borrow_transaction.user.username} - {self.borrow_transaction.item.name} | {self.status}"
