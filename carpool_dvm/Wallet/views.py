from django.shortcuts import render, redirect
from .models import Wallet ,Transaction
from django.contrib import messages
# Create your views here.

def wallet_dashboard_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        if amount > 0 :
            wallet.balance += amount
            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                trx_type='TOP_UP',
                description="Manual Credits Added"
            )

            messages.success(request, f"{amount} added to your wallet!")
        return redirect('wallet_dashboard')
    
    return render(request, 'wallet/wallet_dashboard.html', {"wallet": wallet})