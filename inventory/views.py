from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import FinishedBag, Client, Order
from .forms import FinishedBagForm, ClientForm, OrderForm

# Create your views here.

@login_required
def dashboard(request):
    """
    The main command center view. Fetches key metrics and recent activity.
    """
    # 1. Base Queryset for bags to reuse
    bags = FinishedBag.objects.all()

    # 2. Calculate Key Metrics (KPIs)
    # Use aggregate to calculate the sum directly in the database (much faster)
    total_bales_data = bags.aggregate(Sum('quantity_bales'))
    # Handle the case where there are no bags yet (returns None, so default to 0)
    total_bales = total_bales_data['quantity_bales__sum'] or 0

    low_stock_count = bags.filter(quantity_bales__lt=5).count()
    total_clients = Client.objects.count()
    total_orders = Order.objects.count()

    # 3. Fetch Recent Activity Data
    # Get the 5 most recent orders. use select_related to prevent extra DB queries in the template
    recent_orders = Order.objects.select_related('client', 'bag').order_by('-id')[:5]

    # Get the actual list of items that are critical (lowest stock first), limit to top 5
    critical_stock = bags.filter(quantity_bales__lt=5).order_by('quantity_bales')[:5]

    # 4. Compile context data for the template
    context = {
        'total_bales': total_bales,
        'low_stock_count': low_stock_count,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'critical_stock': critical_stock,
    }

    return render(request, 'inventory/dashboard.html', context)

# --- R: READ (List View) ---
@login_required
def bag_list(request):
    bags = FinishedBag.objects.all().order_by('-last_updated')
    return render(request, 'inventory/bag_list.html', {'bags': bags})

# --- C: CREATE ---
@login_required
def bag_create(request):
    form = FinishedBagForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('bag_list')
    return render(request, 'inventory/bag_form.html', {'form': form, 'title': 'Add New Bag Stock'})

# --- U: UPDATE ---
@login_required
def bag_update(request, pk):
    bag = get_object_or_404(FinishedBag, pk=pk)
    form = FinishedBagForm(request.POST or None, instance=bag)
    if form.is_valid():
        form.save()
        return redirect('bag_list')
    # Reuse the same form template
    return render(request, 'inventory/bag_form.html', {'form': form, 'title': f'Edit: {bag}'})

# --- D: DELETE ---
@login_required
def bag_delete(request, pk):
    bag = get_object_or_404(FinishedBag, pk=pk)
    if request.method == 'POST':
        bag.delete()
        return redirect('bag_list')
    return render(request, 'inventory/bag_confirm_delete.html', {'bag': bag})


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
    return render(request, 'inventory/form_generic.html', {'form': form, 'title': 'Add New Client'})


# ===========================
# ORDER VIEWS (The Dynamic Part)
# ===========================
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'inventory/order_list.html', {'orders': orders})


@login_required
def order_create(request):
    form = OrderForm(request.POST or None)
    # The form.is_valid() call runs the 'clean' method we wrote in forms.py
    # This checks if there is enough stock.
    if form.is_valid():
        # 1. Get the order object but don't save to DB yet
        order = form.save(commit=False)

        # 2. Get the related bag
        bag_being_sold = order.bag

        # 3. AUTOMATICALLY REDUCE STOCK
        # We know stock is sufficient because form.is_valid() passed
        bag_being_sold.quantity_bales = bag_being_sold.quantity_bales - order.quantity_ordered
        bag_being_sold.save()  # Save the updated stock level

        # 4. Now save the order record
        order.save()
        return redirect('order_list')

    return render(request, 'inventory/form_generic.html', {
        'form': form,
        'title': 'Place New Order',
        'helper_text': 'Stock will be deducted automatically.'
    })

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
