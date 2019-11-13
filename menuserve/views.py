from django.shortcuts import render, redirect, reverse
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

import sys

# Create your views here.

def index(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    users = User.objects.all()
    print(users)

    data =  {"user": user, "is_customer": is_customer }

    return render(request, "index.html", data)

def change_quantity(request):
    orders = Order.objects.all()
    order = orders.last()
    try:
        id = request.POST.get('item_id', None)
        item = OrderedItem.objects.get(id=id)
        operation = request.POST.get('operation', None)
        if (operation == "add"):
            item.quantity += 1
            item.save()
            order.total_items += 1
            order.save()
        elif (operation == "remove"):
            item.quantity -= 1
            item.save()
            order.total_items -= 1
            if (item.quantity <= 0):
                item.quantity = 0
                item.save()
                order.items.remove(item)
                item.delete()
            order.save()

        data = { 'quantity': item.quantity }
        return JsonResponse(data)
    except:
        return redirect(reverse("bag"))

def bag(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    if (not is_customer):
        return redirect(reverse("index"))

    items = Item.objects.all()
    locations = Location.objects.all()
    orders = Order.objects.all()

    order = orders.last()

    current_location = get_current_location(locations)
    if current_location != None:
        curr_location = current_location.name
    else:
        curr_location = "CHOOSE LOCATION"

    if request.method == "POST":

        if "place-order" in request.POST:
            try:
                name = request.POST["name"]
                delivery = request.POST["delivery"]
                order.location = current_location
                order.name = name
                order.delivery = delivery
                order.submitted = True
                order.user = user
                order.save()
                bag = Order(user=user)
                bag.save()
                return redirect(reverse("orders"))
            except:
                return redirect(reverse("bag"))

    data = {"locations": locations, "current_location": curr_location,
            "items": items, "orders": orders, "order": order,
            "user": user, "is_customer": is_customer }
    return render(request, "bag.html", data)

def menu(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    items = Item.objects.all()
    orders = Order.objects.all()

    if (user.is_authenticated):
        if orders.exists():
            order = orders.last()
            if (order.user != user):
                order.delete()
                order = Order(user=user)
                order.save()
        else:
            order = Order(user=user)
            order.save()

    if request.method == "POST":
        if "dish" in request.POST:
            id = request.POST["dish"]
            item = Item.objects.get(id=int(id))

        if "snack" in request.POST:
            id = request.POST["snack"]
            item = Item.objects.get(id=int(id))

        if "drink" in request.POST:
            id = request.POST["drink"]
            item = Item.objects.get(id=int(id))

        if "dessert" in request.POST:
            id = request.POST["dessert"]
            item = Item.objects.get(id=int(id))

        try:
            orderedItem = order.items.all().get(item=item)
        except:
            orderedItem = OrderedItem(item=item)

        orderedItem.quantity += 1
        orderedItem.save()

        order.items.add(orderedItem)
        order.total_items += 1
        order.save()

    dishes = Item.objects.filter(category="dish")
    snacks = Item.objects.filter(category="snack")
    drinks = Item.objects.filter(category="drink")
    desserts = Item.objects.filter(category="dessert")

    data = { "dishes": dishes, "snacks": snacks,
            "drinks": drinks, "desserts": desserts,
            "items": items, "orders":orders,
            "user": user, "is_customer": is_customer }
    return render(request, "menu.html", data)

@login_required(login_url='sign-in')
def edit_menu(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    if (not user.is_authenticated or not user.employee.is_manager): return redirect(reverse("index"))

    items = Item.objects.all()

    form = ItemForm()

    if request.method == "POST":

        if "new-item" in request.POST:
            form = ItemForm(request.POST, request.FILES)
            if form.is_valid():
                if "dish" in request.POST:
                    add_item("dish", request, form)
                    return redirect(reverse("edit-menu"))
                if "snack" in request.POST:
                    add_item("snack", request, form)
                    return redirect(reverse("edit-menu"))
                if "drink" in request.POST:
                    add_item("drink", request, form)
                    return redirect(reverse("edit-menu"))
                if "dessert" in request.POST:
                    add_item("dessert", request, form)
                    return redirect(reverse("edit-menu"))

        if "edit" in request.POST:
            try:
                id = request.POST["edit"]
                item = Item.objects.get(id=int(id))
                name_key = "edit-name"+id
                item.name = request.POST[name_key]
                description_key = "edit-description"+id
                item.description = request.POST[description_key]
                price_key = "edit-price"+id
                item.price = request.POST[price_key]
                item.save()
            except:
                return redirect(reverse("edit-menu"))

        if "delete" in request.POST:
            try:
                id = request.POST["delete"]
                item = Item.objects.get(id=int(id))
                item.delete()
            except:
                return redirect(reverse("edit-menu"))

    dishes = Item.objects.filter(category="dish")
    snacks = Item.objects.filter(category="snack")
    drinks = Item.objects.filter(category="drink")
    desserts = Item.objects.filter(category="dessert")

    data = { "dishes": dishes, "snacks": snacks,
            "drinks": drinks, "desserts": desserts,
            "items": items, "form": form, "user": user,
            "is_customer": is_customer }
    return render(request, "edit-menu.html", data)

def add_item(type, request, form):
    image = form.cleaned_data["image"]
    name = form.cleaned_data["name"]
    description = form.cleaned_data["description"]
    price = form.cleaned_data["price"] #"$xx.xx (xxx CAL)"
    item = Item(name=name, description=description,
                    price=price, image=image, category=type)
    item.save()

def refresh_orders_ajax(request):
    data = {  }
    return JsonResponse(data)

def refresh_orders(request):
    user = request.user
    is_customer = not hasattr(user, 'employee')

    locations = Location.objects.all()

    current_location = get_current_location(locations)
    if current_location != None:
        curr_location = current_location
    else:
        curr_location = "CHOOSE LOCATION"

    if (hasattr(user, "employee")):
        if current_location not in user.employee.locations.all():
                return redirect(reverse("locations"))
        orders = Order.objects.filter(submitted=True, location=current_location)
    else:
        orders = Order.objects.filter(submitted=True, location=current_location, user=user)

    data = { 'orders': orders, 'is_customer': is_customer}

    return render(request, "refresh-orders.html", data)

@login_required(login_url='sign-in')
def orders(request):

    user = request.user

    if (hasattr(user, "employee")):
        return employee_orders(request)
    else:
        return customer_orders(request)

@login_required(login_url='sign-in')
def order(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    data =  {"user": user, "is_customer": is_customer }

    return render(request, "order.html", data)

@login_required(login_url='sign-in')
def employee_orders(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    items = Item.objects.all()
    locations = Location.objects.all()

    current_location = get_current_location(locations)
    if current_location != None:
        curr_location = current_location
    else:
        curr_location = "CHOOSE LOCATION"

    if current_location not in user.employee.locations.all():
            return redirect(reverse("locations"))

    if request.method == "POST":
        if "fulfill" in request.POST:
            id = request.POST["fulfill"]
            order = Order.objects.get(id=int(id))
            data = {"order":order,"current_location": curr_location }
            return render(request, "order.html", data)
        if "cancel" in request.POST:
            id = request.POST["cancel"]
            order = Order.objects.get(id=int(id))
            order.delete()
        if "ready" in request.POST:
            id = request.POST["ready"]
            order = Order.objects.get(id=int(id))
            order.fulfilled = True
            order.save()

    orders = Order.objects.filter(submitted=True, location=current_location)

    data = {"locations": locations, "current_location": curr_location,
            "items": items, "orders": orders, "user": user,
            "is_customer": is_customer }
    return render(request, "orders.html", data)

@login_required(login_url='sign-in')
def customer_orders(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    items = Item.objects.all()
    locations = Location.objects.all()

    current_location = get_current_location(locations)
    if current_location != None:
        curr_location = current_location
    else:
        curr_location = "CHOOSE LOCATION"

    if request.method == "POST":
        if "cancel" in request.POST:
            id = request.POST["cancel"]
            order = Order.objects.get(id=int(id))
            order.delete()


    orders = Order.objects.filter(submitted=True, location=current_location, user=user)

    data = {"locations": locations, "current_location": curr_location,
            "items": items, "orders": orders, "user": user,
            "is_customer": is_customer }
    return render(request, "orders.html", data)

def locations(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    locations = Location.objects.all()
    current_location = get_current_location(locations)

    if request.method == "POST":
        if "location" in request.POST:
            if current_location != None:
                current_location.active = False
                current_location.save()
            id = request.POST["location"]
            new_current_location = Location.objects.get(id=int(id))
            new_current_location.active = True
            new_current_location.save()
            return redirect(reverse("locations"))

    data = {"locations":locations, "user": user, "is_customer": is_customer }

    return render(request, "locations.html", data)

def get_current_location(locations):
    current_location = None
    for location in locations:
        if location.active == True:
            current_location = location
    return current_location

@login_required(login_url='sign-in')
def portal(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    if (not user.is_authenticated or not user.employee.is_manager): return redirect(reverse("index"))

    locations = Location.objects.all()
    employees = Employee.objects.all()
    users = User.objects.all()

    form = EmployeeForm()

    if request.method == "POST":
        if "delete-location" in request.POST:
            try:
                id = request.POST.get("delete-location")
                location = Location.objects.get(id=int(id))
                location.delete()
            except:
                return redirect(reverse("portal"))
        if "add-location" in request.POST:
            name = request.POST.get("location")
            location = Location(name=name)
            location.save()

        if "delete-location-employee" in request.POST:
            try:
                value = request.POST.get("delete-location-employee").split(":")
                employee_id = int(value[0])
                location_id = int(value[1])
                user = User.objects.get(id=int(employee_id))
                employee = user.employee
                location = Location.objects.get(id=int(location_id))
                employee.locations.remove(location)
            except:
                return redirect(reverse("portal"))

        if "add_manager" in request.POST or "add_employee" in request.POST:
            form = EmployeeForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data["image"]
                user = form.cleaned_data["user"]
                if (hasattr(user, 'employee')):
                    if "add_manager" in request.POST:
                        employee = Employee(user=user, name=user.get_full_name(),
                            image=image, is_manager=True)
                    else:
                        employee = Employee(user=user, name=user.get_full_name(),
                            image=image, is_manager=False)
                    employee.save()
                return redirect(reverse("portal"))


        if "delete" in request.POST:
            try:
                id = request.POST["delete"]
                user = User.objects.get(id=id)
                employee = user.employee
                employee.delete()
            except:
                return redirect(reverse("portal"))

    managers = Employee.objects.filter(is_manager=True).all()
    employees = Employee.objects.filter(is_manager=False).all()

    data = {"locations": locations, "managers": managers,
            "employees": employees, "form": form,
            "user": user, "is_customer": is_customer }
    return render(request, "portal.html", data)

def add_location_to_employee(request, id):
    locations = Location.objects.all()

    if request.method == "POST":
        location_name = request.POST.get("location")
        try:
            location = Location.objects.get(name=location_name)
            user = User.objects.get(id=id)
            employee = user.employee
            employee.locations.add(location)
        except:
            redirect(reverse("portal"))

    managers = Employee.objects.filter(is_manager=True).all()
    employees = Employee.objects.filter(is_manager=False).all()

    data = {"locations": locations, "managers": managers,
            "employees": employees}
    return redirect(reverse("portal"))

def sign_in(request):

    user = request.user
    is_customer = not hasattr(user, 'employee')

    users = User.objects.all()
    employees = Employee.objects.all()

    form = None;

    if request.method == "POST":

        if "login" in request.POST:
            form = LoginForm(request.POST, request.FILES)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(reverse("menu"))
                else:
                    return redirect(reverse("sign-in"))

        if "register" in request.POST:
            form = RegisterForm(request.POST, request.FILES)
            if form.is_valid():
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                try:
                    user = User.objects.create_user(username, None, password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect(reverse("menu"))
                except:
                    return redirect(reverse("sign-in"))

    data = {"is_customer": is_customer, "form": form, }
    return render(request, "sign-in.html", data)

def logout_view(request):
    logout(request)
    return redirect(reverse("sign-in"))
