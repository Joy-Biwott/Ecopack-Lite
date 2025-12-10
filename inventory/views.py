from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # <--- NEW: Needed for user_list
from django.contrib import messages
from django.db.models import Sum
from .models import FinishedBag, Client, Order, Feedback
from .forms import FinishedBagForm, ClientForm, OrderForm, FeedbackForm


# ===========================
# DASHBOARD (The Cockpit)
# ===========================
@login_required
def dashboard(request):
    bags = FinishedBag.objects.all()

    # 1. Metrics
    total_bales_data = bags.aggregate(Sum('quantity_bales'))
    total_bales = total_bales_data['quantity_bales__sum'] or 0

    low_stock_count = bags.filter(quantity_bales__lte=10).count()
    total_clients = Client.objects.count()
    total_orders = Order.objects.count()

    # 2. Recent Activity
    recent_orders = Order.objects.select_related('client', 'bag').order_by('-id')[:5]
    critical_stock = bags.filter(quantity_bales__lte=10).order_by('quantity_bales')[:5]

    context = {
        'total_bales': total_bales,
        'low_stock_count': low_stock_count,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'critical_stock': critical_stock,
    }
    return render(request, 'inventory/dashboard.html', context)


# ===========================
# INVENTORY (Bags)
# ===========================
@login_required
def bag_list(request):
    bags = FinishedBag.objects.all().order_by('-last_updated')
    return render(request, 'inventory/bag_list.html', {'bags': bags})


@login_required
def bag_create(request):
    form = FinishedBagForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('bag_list')
    return render(request, 'inventory/bag_form.html', {'form': form, 'title': 'Add New Bag Stock'})


@login_required
def bag_update(request, pk):
    bag = get_object_or_404(FinishedBag, pk=pk)
    form = FinishedBagForm(request.POST or None, instance=bag)
    if form.is_valid():
        form.save()
        return redirect('bag_list')
    return render(request, 'inventory/bag_form.html', {'form': form, 'title': f'Edit: {bag}'})


@login_required
def bag_delete(request, pk):
    bag = get_object_or_404(FinishedBag, pk=pk)
    if request.method == 'POST':
        bag.delete()
        return redirect('bag_list')
    return render(request, 'inventory/bag_confirm_delete.html', {'bag': bag})


# ===========================
# CLIENTS
# ===========================
@login_required
def client_list(request):
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'inventory/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('client_list')
    return render(request, 'inventory/client_form.html', {'form': form, 'title': 'Add New Client'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        return redirect('client_list')
    return render(request, 'inventory/client_form.html', {'form': form, 'title': f'Edit: {client.name}'})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'inventory/client_confirm_delete.html', {'client': client})


# ===========================
# ORDERS
# ===========================
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'inventory/order_list.html', {'orders': orders})


@login_required
def order_create(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        order = form.save(commit=False)
        bag_being_sold = order.bag
        bag_being_sold.quantity_bales = bag_being_sold.quantity_bales - order.quantity_ordered
        bag_being_sold.save()
        order.save()
        return redirect('order_list')

    return render(request, 'inventory/form_generic.html', {
        'form': form,
        'title': 'Place New Order',
        'helper_text': 'Stock will be deducted automatically.'
    })


# ===========================
# AUTH & ADMIN MODULES
# ===========================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def user_list(request):
    # This view fixes the 'NoReverseMatch' error
    # Security: Only Admins can see this
    if not request.user.is_superuser and getattr(request.user.profile, 'role', '') != 'Admin':
        messages.error(request, "Access Denied: Admin rights required.")
        return redirect('dashboard')

    users = User.objects.all().select_related('profile').order_by('date_joined')
    return render(request, 'inventory/user_list.html', {'users': users})


# ===========================
# FEEDBACK / DEV LOG
# ===========================
@login_required
def feedback_create(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you! Your suggestion has been submitted.')
            return redirect('dashboard')
    else:
        form = FeedbackForm()
    return render(request, 'inventory/feedback_form.html', {'form': form})


@login_required
def feedback_list(request):
    # Security: Only Admins can see the Dev Log
    if not request.user.is_superuser and getattr(request.user.profile, 'role', '') != 'Admin':
        messages.error(request, "Access Denied.")
        return redirect('dashboard')

    issues = Feedback.objects.all().order_by('-created_at')
    return render(request, 'inventory/feedback_list.html', {'issues': issues})