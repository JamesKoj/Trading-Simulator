from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import Trader
from django.contrib import messages
from .helpers import lookup, usd
from .models import Transaction

# Create your views here.
@login_required(login_url='users/login')
def index(request):
    """Show portfolio of stocks"""

    current_user = request.user
    user_portfolio = Transaction.objects.values('symbol', "companyName").filter(trader=current_user).\
        annotate(share_quantity=Sum("quantity"))

    stocks = []
    stocks_subtotal = 0

    for row in user_portfolio:
        if int(row["share_quantity"]) >= 1:
            current_price = float(lookup(row["symbol"])["price"])
            row_dict = {
                "symbol": row["symbol"],
                "name": row["companyName"],
                "shares": row["share_quantity"],
                "price": usd(current_price),
                "total": usd(int(row["share_quantity"]) * current_price)
            }

            stocks.append(row_dict)

            stocks_subtotal += int(row["share_quantity"]) * current_price

    current_user = request.user
    current_trader = Trader.objects.get(trader=current_user)
    current_cash = current_trader.cash

    total = usd(stocks_subtotal + current_cash)

    usd_cash = usd(current_cash)

    context = {
        "stocks": stocks,
        "stocks_subtotal": stocks_subtotal,
        "current_cash": current_cash,
        "total": total,
        "usd_cash": usd_cash
    }

    return render(request, 'tradingplatform/index.html', context)


@login_required(login_url='users/login')
def buy(request):
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol_dict = lookup(request.POST.get("symbol"))

        try:
            shares_int = int(request.POST.get("shares"))
        except:
            messages.warning(request, "Invalid Share Quantity")
            return render(request, 'tradingplatform/buy.html')

        if symbol_dict is None:
            messages.warning(request, "Invalid Symbol")
            return render(request, 'tradingplatform/buy.html')

        if shares_int < 1 or int(request.POST.get("shares")) != float(request.POST.get("shares")):
            messages.warning(request, "Invalid Share Quantity")
            return render(request, 'tradingplatform/buy.html')

        current_user = request.user
        current_trader = Trader.objects.get(trader=current_user)
        current_cash = current_trader.cash

        if (symbol_dict["price"] * shares_int) <= current_cash:
            current_cash -= (symbol_dict["price"] * shares_int)

            new_trade = Transaction(trader=current_user, symbol=symbol_dict["symbol"], companyName=symbol_dict["name"],
                                    quantity=shares_int, price=symbol_dict["price"])
            new_trade.save()
            current_trader.cash = current_cash
            current_trader.save()

            return redirect('/index')

        else:
            messages.warning(request, "Invalid Share Quantity")
            return render(request, 'tradingplatform/buy.html')

    else:
        return render(request, 'tradingplatform/buy.html')


@login_required(login_url='users/login')
def sell(request):
    """Sell shares of stock"""

    # list the stock ticker symbols currently in the user's portfolio
    symbols = Transaction.objects.values('symbol').filter(trader=request.user). \
        annotate(share_quantity=Sum("quantity")).filter(share_quantity__gt=0)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.POST.get("symbol")

        if symbol is None:
            messages.warning(request, "Invalid Symbol")
            return render(request, 'tradingplatform/sell.html', {"symbols": symbols})

        if request.POST.get("shares") == "":
            messages.warning(request, "Invalid Share Quantity")
            return render(request, 'tradingplatform/sell.html', {"symbols": symbols})

        symbol_dict = lookup(request.POST.get("symbol"))
        shares_int = int(request.POST.get("shares")) * -1

        current_user = request.user
        current_trader = Trader.objects.get(trader=current_user)
        transactions = Transaction.objects.values('symbol').\
            filter(trader=current_user, symbol=symbol).annotate(share_quantity=Sum("quantity"))

        current_quantity = int(transactions[0]["share_quantity"])

        if symbol_dict is None:
            messages.warning(request, "Invalid Symbol")
            return render(request, 'tradingplatform/sell.html', {"symbols": symbols})

        if ((shares_int * -1) > current_quantity) or (shares_int >= 0):
            messages.warning(request, "Invalid Share Quantity")
            return render(request, 'tradingplatform/sell.html', {"symbols": symbols})

        current_cash = current_trader.cash

        if (symbol_dict["price"] * shares_int) < current_cash:
            current_cash -= (symbol_dict["price"] * shares_int)

            new_trade = Transaction(trader=current_user, symbol=symbol_dict["symbol"],
                                    companyName=symbol_dict["name"], quantity=shares_int, price=symbol_dict["price"])
            new_trade.save()
            current_trader.cash = current_cash
            current_trader.save()

            return redirect('/index')

    else:
        return render(request, "tradingplatform/sell.html", {"symbols": symbols})


@login_required(login_url='users/login')
def history(request):
    """Show history of transactions"""

    current_user = request.user

    # get all the current user's transactions
    user_transactions = Transaction.objects.filter(trader=current_user)

    return render(request, 'tradingplatform/history.html', {"user_transactions": user_transactions})


@login_required(login_url='users/login')
def quote(request):
    """Get stock quote."""

    if request.method == 'POST':

        if lookup(request.POST.get("symbol")) is None:
            messages.warning(request, "Not a Valid Symbol")
            return render(request, 'tradingplatform/quote.html')

        else:
            quote_dict = lookup(request.POST["symbol"])
            context = {
                "name": quote_dict["name"],
                "price": usd(quote_dict["price"]),
                "symbol": quote_dict["symbol"]
            }
            return render(request, 'tradingplatform/quoted.html', context)
    else:
        return render(request, 'tradingplatform/quote.html')


@login_required(login_url='users/login')
def quoted(request):
    return render(request, 'tradingplatform/quoted.html')
