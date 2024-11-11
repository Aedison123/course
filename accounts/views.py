from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Cart, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from .forms import StaffSignupForm, StaffLoginForm,userLoginForm
from .models import CartItem
from .forms import ProductForm
from .models import Product
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import CartItem, Product
from django.contrib.auth import authenticate , logout,login

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Product
from django.contrib.auth.decorators import login_required

def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in
            login(request, user)
            
            # Redirect to the dashboard view
            return redirect('accounts:dash')  # Ensure this matches the URL name for the dashboard
        else:
            # Authentication failed, show an error message
            messages.error(request, 'Invalid credentials')

    # If not POST, render the login page
    return render(request, 'index.html')


# accounts/views.py

@login_required
def dashboard_view(request):
    # Get the approved products from the database
    products = Product.objects.filter(is_approved=True)
    
    # Render the dashboard template with the list of products
    return render(request, 'dash.html', {'products': products})

def product_list(request):
    if not request.user.is_authenticated:
        return redirect('accounts:index') 
    products = Product.objects.all()  # Get all products from the database
    return render(request, 'product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Include request.FILES for image upload
        if form.is_valid():
            form.save()
            return redirect('accounts:product_list')  # Adjust this to your actual product list view name
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})



def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # This will return a 404 if the product doesn't exist
    product.delete()
    return redirect('accounts:product_list')  # Redirect to the product list after deletion

#
# Logout view
def user_logout(request):
    logout(request)  # Log the user out (clear session)
    return redirect('accounts:index')  # Redirect to login page after logout


def staff_signup(request):
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            return redirect('accounts:staff_login')  # Redirect to login after signup
    else:
        form = StaffSignupForm()
    
    return render(request, 'staff_signup.html', {'form': form})

def staff_login(request):
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:product_list')  # Ensure this URL pattern exists
            else:
                # Invalid login
                form.add_error(None, "Invalid username or password.")
    else:
        form = StaffLoginForm()
    
    return render(request, 'staff_login.html', {'form': form})

def staff_logout(request):
    logout(request)
    return redirect('accounts:staff_login')  # Redirect to login after logout


# views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    # Logout the user and clear session
    logout(request)
    
    # Set session expiry to immediately expire
    request.session.set_expiry(0)  # Forces session to expire immediately

    # Redirect to the login page
    return redirect('login')


from .models import Product  # Ensure this import is correct

def home(request):
    # Fetch approved products only
    products = Product.objects.filter(is_approved=True)

    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('accounts:index')  # Redirect to login page if user is not logged in

    # If the user is authenticated, render the homepage with the products context
    return render(request, 'home.html', {'products': products})
def search_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:index')  
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'index.html', {'products': results})

def search_viewH(request):
    if not request.user.is_authenticated:
        return redirect('accounts:index')  
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'home.html', {'products': results})



def about(request):
    if not request.user.is_authenticated:
        return redirect('accounts:index')  
    return render(request,'about.html')


    
def register_view(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:index')  # Redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})



# views.py



# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)  # Create cart if it doesn't exist

#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#     if not created:  # If the item is already in the cart, increase the quantity
#         cart_item.quantity += 1
#         cart_item.save()

#     return redirect('accounts:cart_view')  # Redirect to cart view


# def cart_view(request):
#     cart = Cart.objects.get_or_create(user=request.user)[0]  # Get or create the user's cart
#     cart_items = CartItem.objects.filter(cart=cart)  # Fetch cart items for the user's cart
#     total = sum(item.product.price * item.quantity for item in cart_items)  # Calculate total

#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'total': total,
#     })

# # views.py




from django.shortcuts import redirect
from django.views.generic import DetailView
from .models import Product

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated, if not redirect to the home page
        if not request.user.is_authenticated:
            return redirect('accounts:index')  # Adjust the redirect URL as needed
        return super().dispatch(request, *args, **kwargs)





def edit_product(request, product_id):
    # Retrieve the product or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Get data from the form (name and other fields)
        product.name = request.POST.get('name', product.name)

        # Handle image upload if provided
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        # Handle video upload if provided (using a field that corresponds to the video)
        if 'video' in request.FILES:
            product.video = request.FILES['video']   # Assuming your model has a 'video' field

        # Save the updated product
        try:
            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('accounts:product_list')  # Redirect to the product list
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')

    # Render the edit product template with the product instance
    return render(request, 'edit_product.html', {'product': product})






@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))

        # Update the cart item quantity
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate the new total
        total = sum(item.product.price * item.quantity for item in CartItem.objects.all())

        return JsonResponse({'total': total})

    return JsonResponse({'error': 'Invalid request'}, status=400)



