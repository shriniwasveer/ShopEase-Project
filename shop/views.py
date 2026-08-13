from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Category, Product, Order, OrderItem
from .forms import UserRegisterForm, CheckoutForm

def home_view(request):
    categories = Category.objects.all()[:5]
    featured_products = Product.objects.filter(is_featured=True)[:4]
    popular_products = Product.objects.filter(is_popular=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'popular_products': popular_products,
    }
    return render(request, 'home.html', context)


def product_list_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)

    sort_by = request.GET.get('sort', '')
    if sort_by == 'low_high':
        products = products.order_by('price')
    elif sort_by == 'high_low':
        products = products.order_by('-price')
    elif sort_by == 'latest':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'selected_sort': sort_by,
    }
    return render(request, 'products.html', context)


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            first_name = form.cleaned_data.get('full_name')
            user.first_name = first_name
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            messages.success(request, "Account created successfully! You can now login.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check form errors.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'profile.html', {'orders': orders})


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = float(product.final_price) * item_data['quantity']
            subtotal += item_total
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue

    delivery_charge = 50.00 if subtotal > 0 and subtotal < 500 else 0.00
    grand_total = subtotal + delivery_charge

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product.stock < quantity:
        messages.error(request, f"Sorry, only {product.stock} units available in stock.")
        return redirect(request.META.get('HTTP_REFERER', 'products'))

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {'quantity': quantity}

    request.session['cart'] = cart
    messages.success(request, f"Added {product.name} to your cart!")
    return redirect(request.META.get('HTTP_REFERER', 'products'))


def update_cart_view(request, product_id):
    action = request.POST.get('action')
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        if action == 'increase':
            product = get_object_or_404(Product, id=product_id)
            if cart[str(product_id)]['quantity'] < product.stock:
                cart[str(product_id)]['quantity'] += 1
            else:
                messages.warning(request, "Maximum stock limit reached.")
        elif action == 'decrease':
            cart[str(product_id)]['quantity'] -= 1
            if cart[str(product_id)]['quantity'] <= 0:
                del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart_view(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.info(request, "Item removed from cart.")
    return redirect('cart')


def clear_cart_view(request):
    if 'cart' in request.session:
        del request.session['cart']
        messages.info(request, "Cart cleared successfully.")
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty. Add products before checking out.")
        return redirect('products')

    cart_items = []
    subtotal = 0

    for product_id, item_data in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = float(product.final_price) * item_data['quantity']
        subtotal += item_total
        cart_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'item_total': item_total,
        })

    delivery_charge = 50.00 if subtotal > 0 and subtotal < 500 else 0.00
    grand_total = subtotal + delivery_charge

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = grand_total
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].final_price
                )
                item['product'].stock -= item['quantity']
                item['product'].save()

            del request.session['cart']
            messages.success(request, f"Order Placed Successfully! Order ID: {order.order_id}")
            return redirect('order_detail', order_id=order.order_id)
    else:
        initial_data = {
            'full_name': f"{request.user.first_name}".strip() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    }
    return render(request, 'checkout.html', context)


@login_required
def orders_list_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})