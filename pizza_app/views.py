from django.shortcuts import render
from django.utils import timezone
from .models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Commands for Django management
# python3 manage.py create_groups  
# python3 manage.py runserver 0.0.0.0:8000
# python3 manage.py makemigrations
# python3 manage.py migrate 
# daphne -b 0.0.0.0 -p 8000 pizza_manage.asgi:application

def fetch_orders(request):
    orders_today = Order.objects.filter(order_date__date=timezone.now().date()).prefetch_related('items')
    order_data = []

    for order in orders_today:
        items = [{"name": item.menu_item.name, "quantity": item.quantity , "comment": item.comment , "typ":str(item.menu_item.typ) } for item in order.items.all()]
        order_data.append({
            "id": order.id,
            "table_number": f'Table {order.table.number}' if order.table else "N/A",
            "items": items,
            "order_date": order.order_date.strftime('%Y-%m-%d %H:%M'),
            "status": order.status,
            "total_price": str(order.total_price)  # Convert to string for JSON serialization
        })

    return JsonResponse({"orders": order_data})


def home(request):
    # Get today's date
    to_day = timezone.now().date()
    
    # Filter orders by today's date
    orders_today = Order.objects.filter(order_date__date=to_day)

    context = {
        'orders_today': orders_today,
    }
    return render(request, 'index3.html', context)

def order_system(request):
    menu = Menu.objects.all()
    tables = Table.objects.all()
    typ = Typ.objects.all()
    return render(request,'table.html', {'menus': menu , 'tables': tables , 'typs':typ})

def chef_view(request):
    return render(request, 'chef.html')

@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_number = data.get('table_number')
            items = data.get('items')
            total_price = data.get('total_price')

            table = get_object_or_404(Table, number=table_number)
            order = Order.objects.create(table=table, total_price=total_price)

            for item in items:
                menu_item = get_object_or_404(Menu, id=item['name'])
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item['quantity'],
                    comment=item.get('comment', '')
                )

            # Notify chef via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "orders",
                {
                    'type': 'order_message',
                    'message': f"New order for Table {table_number} "

                }
            )

            return JsonResponse({"message": "Order submitted successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)