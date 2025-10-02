from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.utils import timezone

from .forms import SignUpForm, BorrowForm
from .models import Profile, Item, BorrowTransaction, Penalty
from django.contrib.auth.models import User

# --------- Auth Views ---------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create Profile
            department = form.cleaned_data['department']
            id_number = form.cleaned_data['id_number']
            Profile.objects.create(user=user, department=department, id_number=id_number)

            messages.success(request, "Account created successfully! Please sign in.")
            return redirect('signin')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'user_dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'user/signin.html')

def signout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signin')

# --------- Dashboards ---------
@login_required
def user_dashboard(request):
    # Check overdue borrows and create penalties
    check_and_create_penalties(request.user)
    return render(request, 'user/dashboard.html')

@login_required
def admin_dashboard(request):
    # Admin can also check overdue borrows globally
    check_and_create_penalties()
    return render(request, 'admin/dashboard.html')


# --------- Admin check ---------
def admin_check(user):
    return user.is_staff

# --------- Admin User Management ---------
@user_passes_test(admin_check)
def admin_users(request):
    users = User.objects.filter(is_staff=False)

    # --- Add User ---
    if request.method == 'POST' and 'add_user' in request.POST:
        username = request.POST.get('username')
        email = request.POST.get('email')
        department = request.POST.get('department')
        id_number = request.POST.get('id_number')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password, is_staff=False)
                Profile.objects.create(user=user, department=department, id_number=id_number)
            messages.success(request, "User added successfully.")
        return redirect('admin_users')

    # --- Edit User ---
    if request.method == 'POST' and 'edit_user' in request.POST:
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        profile = user.profile

        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        profile.department = request.POST.get('department')
        profile.id_number = request.POST.get('id_number')

        with transaction.atomic():
            user.save()
            profile.save()
        messages.success(request, "User updated successfully.")
        return redirect('admin_users')

    # --- Delete User ---
    if request.method == 'POST' and 'delete_user' in request.POST:
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('admin_users')

    return render(request, 'admin/admin_users.html', {'users': users})

# --------- Admin Item Management ---------
@user_passes_test(admin_check)
def admin_items(request):
    items = Item.objects.all()

    # --- Add Item ---
    if request.method == 'POST' and 'add_item' in request.POST:
        name = request.POST.get('name')
        item_type = request.POST.get('item_type')
        serial_number = request.POST.get('serial_number')
        condition = request.POST.get('condition')
        stock = request.POST.get('stock', 0)

        if Item.objects.filter(serial_number=serial_number).exists():
            messages.error(request, "Item with this serial number already exists.")
        else:
            Item.objects.create(name=name, item_type=item_type, serial_number=serial_number,
                                condition=condition, stock=stock)
            messages.success(request, "Item added successfully.")
        return redirect('admin_items')

    # --- Edit Item ---
    if request.method == 'POST' and 'edit_item' in request.POST:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)

        item.name = request.POST.get('name')
        item.item_type = request.POST.get('item_type')
        item.serial_number = request.POST.get('serial_number')
        item.condition = request.POST.get('condition')
        item.stock = request.POST.get('stock', item.stock)
        item.save()
        messages.success(request, "Item updated successfully.")
        return redirect('admin_items')

    # --- Delete Item ---
    if request.method == 'POST' and 'delete_item' in request.POST:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('admin_items')

    return render(request, 'admin/admin_items.html', {'items': items})


# --------- Borrowing System (User side) ---------
@login_required
def browse_items(request):
    items = Item.objects.filter(stock__gt=0)
    return render(request, "user/browse_items.html", {"items": items})

@login_required
def borrow_request(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.user = request.user
            borrow.status = "Pending"
            borrow.save()
            messages.success(request, "Borrow request submitted.")
            return redirect("my_borrows")
    else:
        form = BorrowForm(initial={'item': item})
    return render(request, "user/borrow_request.html", {"form": form, "item": item})

@login_required
def my_borrows(request):
    borrows = BorrowTransaction.objects.filter(user=request.user)
    return render(request, "user/my_borrows.html", {"borrows": borrows})


# --------- Borrowing System (Admin side) ---------
@user_passes_test(admin_check)
def manage_borrows(request):
    borrows = BorrowTransaction.objects.all()
    return render(request, "admin/manage_borrows.html", {"borrows": borrows})

@user_passes_test(admin_check)
def approve_borrow(request, borrow_id):
    borrow = get_object_or_404(BorrowTransaction, id=borrow_id)
    if borrow.item.stock >= borrow.quantity:
        borrow.item.stock -= borrow.quantity
        borrow.item.save()
        borrow.status = "Borrowed"
        borrow.save()
        messages.success(request, "Borrow request approved.")
    else:
        messages.error(request, "Not enough stock.")
    return redirect("manage_borrows")

@user_passes_test(admin_check)
def return_item(request, borrow_id):
    borrow = get_object_or_404(BorrowTransaction, id=borrow_id)
    borrow.item.stock += borrow.quantity
    borrow.item.save()
    borrow.status = "Returned"
    borrow.save()
    messages.success(request, "Item marked as returned.")
    return redirect("manage_borrows")


# --------- Penalty System ---------
@login_required
def user_penalties(request):
    penalties = Penalty.objects.filter(borrow_transaction__user=request.user)
    return render(request, "user/penalties.html", {"penalties": penalties})

@user_passes_test(admin_check)
def admin_penalties(request):
    penalties = Penalty.objects.all()
    if request.method == "POST":
        penalty_id = request.POST.get("penalty_id")
        penalty = get_object_or_404(Penalty, id=penalty_id)
        penalty.status = "Paid"
        penalty.paid_at = timezone.now()
        penalty.save()
        messages.success(request, f"Penalty for {penalty.borrow_transaction.user.username} marked as paid.")
        return redirect("admin_penalties")
    return render(request, "admin/penalties.html", {"penalties": penalties})


# --------- Utility: Check Overdue Borrows and Create Penalties ---------
def check_and_create_penalties(user=None):
    if user:
        borrows = BorrowTransaction.objects.filter(user=user, status__in=['Borrowed', 'Approved'])
    else:
        borrows = BorrowTransaction.objects.filter(status__in=['Borrowed', 'Approved'])
    
    for borrow in borrows:
        if borrow.is_overdue():
            borrow.status = 'Overdue'
            borrow.save()
            # Create penalty if it doesn't exist
            if not hasattr(borrow, 'penalty'):
                days_overdue = (timezone.now().date() - borrow.due_date).days
                amount = days_overdue * 50  # Example: 50 per day overdue
                Penalty.objects.create(borrow_transaction=borrow, amount=amount)
