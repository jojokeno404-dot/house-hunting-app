# ====================== MPESA VIEWS ======================

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
import base64
from datetime import datetime
import json
from .models import Apartment, MpesaPayment
from .forms import ApartmentForm

mpesa = None  # You can still use django-daraja if you want, but manual is fine


def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=(consumer_key, consumer_secret), timeout=10)
        r.raise_for_status()
        return r.json().get('access_token')
    except Exception as e:
        print("Access Token Error:", e)
        return None


def format_phone(phone):
    """Standardize Kenyan phone number"""
    phone = phone.strip().replace(" ", "")
    if phone.startswith('0'):
        return '254' + phone[1:]
    elif phone.startswith('254'):
        return phone
    else:
        return '254' + phone


@login_required
def pay_for_agent_details(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    if MpesaPayment.objects.filter(user=request.user, apartment=apartment, paid=True).exists():
        return redirect('show_agent_details', apartment_id=apartment_id)

    return render(request, 'pay_for_details.html', {
        'apartment': apartment,
        'amount': 1,   # Change to real amount later
    })


@login_required
def initiate_mpesa_payment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        if not phone:
            messages.error(request, "Phone number is required")
            return redirect('pay_for_agent_details', apartment_id=apartment_id)

        phone = format_phone(phone)
        amount = 1  # KSh 1 for testing

        access_token = get_mpesa_access_token()
        if not access_token:
            messages.error(request, "Could not connect to M-Pesa.")
            return redirect('pay_for_agent_details', apartment_id=apartment_id)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"APT{apartment.id}",
            "TransactionDesc": f"Payment for {apartment.title}"
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
                timeout=15
            )

            print("STK Push Response:", response.status_code, response.text)
            resp = response.json()

            if resp.get('ResponseCode') == '0':
                checkout_id = resp.get('CheckoutRequestID')

                # ✅ FIXED: Update existing record or create new one
                payment, created = MpesaPayment.objects.update_or_create(
                    user=request.user,
                    apartment=apartment,
                    defaults={
                        'amount': amount,
                        'phone_number': phone,
                        'checkout_request_id': checkout_id,
                        'status': "Pending",
                        'paid': False,
                        'mpesa_receipt_number': None,
                    }
                )

                messages.success(request, "✅ Check your phone for the M-Pesa prompt!")
                return redirect('payment_processing', apartment_id=apartment_id)

            else:
                error = resp.get('ResponseDescription', 'Unknown error')
                messages.error(request, f"M-Pesa Error: {error}")

        except Exception as e:
            print("STK Push Exception:", str(e))
            messages.error(request, "Failed to initiate payment. Please try again.")

    return redirect('pay_for_agent_details', apartment_id=apartment_id)

def apartment_list(request):      # ← Must be here
    apartments = Apartment.objects.all()
    # ... your filtering code
    return render(request, 'apartments.html', {'apartments': apartments})

@login_required
def payment_processing(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    payment = MpesaPayment.objects.filter(
        user=request.user,
        apartment=apartment
    ).order_by('-created_at').first()

    if payment and payment.paid:
        return redirect('show_agent_details', apartment_id=apartment_id)

    return render(request, 'payment_processing.html', {
        'apartment': apartment,
        'payment': payment
    })


@login_required
def show_agent_details(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    if not MpesaPayment.objects.filter(user=request.user, apartment=apartment, paid=True).exists():
        messages.error(request, "You must complete payment first.")
        return redirect('pay_for_agent_details', apartment_id=apartment_id)

    return render(request, 'agent_details.html', {'apartment': apartment})


# ====================== CALLBACK ======================
@csrf_exempt
def mpesa_callback(request):
    print("\n=== MPESA CALLBACK RECEIVED ===")
    print("Request Body:", request.body)

    try:
        data = json.loads(request.body)
        stk = data.get('Body', {}).get('stkCallback', {})
        result_code = stk.get('ResultCode')
        checkout_id = stk.get('CheckoutRequestID')

        print("Checkout ID:", checkout_id)
        print("Result Code:", result_code)

        payment = MpesaPayment.objects.filter(checkout_request_id=checkout_id).first()

        if not payment:
            print("Payment record not found for CheckoutRequestID:", checkout_id)
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            items = stk.get('CallbackMetadata', {}).get('Item', [])

            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')
                elif item.get('Name') == 'TransactionDate':
                    payment.transaction_date = timezone.now()

            payment.paid = True
            payment.status = "Completed"
            payment.save()

            print(f"✅ Payment SUCCESS for {payment.user} - Apartment {payment.apartment}")
        else:
            payment.status = "Failed"
            payment.save()
            print(f"❌ Payment FAILED: {stk.get('ResultDesc')}")

    except Exception as e:
        print("Callback Error:", str(e))

    # Always return success to Safaricom
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    # Check if user has already paid
    has_paid = MpesaPayment.objects.filter(
        user=request.user,
        apartment=apartment,
        paid=True
    ).exists()

    return render(request, 'apartment_detail.html', {
        'apartment': apartment,
        'has_paid': has_paid
    })
@login_required
def add_apartment(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.owner = request.user
            apartment.save()
            return redirect('apartment_list')
    else:
        form = ApartmentForm()

    return render(request, 'add_apartment.html', {'form': form})