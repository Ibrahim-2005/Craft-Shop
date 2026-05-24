from collections import defaultdict

from sqlalchemy import extract, func

from app import db
from app.models.category import Category
from app.models.order import MaterialCost, Order, OrderStatus
from app.models.product import Product


def dashboard_metrics():
    active_orders = Order.query.filter(Order.status != OrderStatus.CANCELLED.value).all()
    all_orders = Order.query.all()
    revenue = sum(float(order.selling_price or 0) for order in active_orders)
    expense = sum(order.total_cost for order in active_orders)
    profit = revenue - expense
    return {
        "total_orders": len(active_orders),
        "cancelled_orders": Order.query.filter_by(status=OrderStatus.CANCELLED.value).count(),
        "all_orders": len(all_orders),
        "total_revenue": revenue,
        "total_expense": expense,
        "total_profit": profit,
        "pending_orders": Order.query.filter_by(status=OrderStatus.PENDING.value).count(),
        "delivered_orders": Order.query.filter_by(status=OrderStatus.DELIVERED.value).count(),
    }


def monthly_finance():
    buckets = defaultdict(lambda: {"revenue": 0, "expense": 0, "profit": 0, "orders": 0})
    for order in Order.query.filter(Order.status != OrderStatus.CANCELLED.value).order_by(Order.created_at).all():
        label = order.created_at.strftime("%b %Y")
        revenue = float(order.selling_price or 0)
        expense = order.total_cost
        buckets[label]["revenue"] += revenue
        buckets[label]["expense"] += expense
        buckets[label]["profit"] += revenue - expense
        buckets[label]["orders"] += 1
    return [{"month": month, **values} for month, values in buckets.items()]


def monthly_insights(finance_rows=None):
    rows = finance_rows if finance_rows is not None else monthly_finance()
    empty = {
        "current_month": "No sales yet",
        "current_revenue": 0,
        "current_expense": 0,
        "current_profit": 0,
        "current_orders": 0,
        "current_margin": 0,
        "average_order_value": 0,
        "best_month": "No sales yet",
        "best_month_profit": 0,
        "growth_rate": 0,
    }
    if not rows:
        return empty

    current = rows[-1]
    previous = rows[-2] if len(rows) > 1 else None
    revenue = float(current["revenue"] or 0)
    profit = float(current["profit"] or 0)
    orders = int(current.get("orders") or 0)
    previous_revenue = float(previous["revenue"] or 0) if previous else 0
    growth = ((revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0
    best = max(rows, key=lambda row: row["profit"])

    return {
        "current_month": current["month"],
        "current_revenue": revenue,
        "current_expense": float(current["expense"] or 0),
        "current_profit": profit,
        "current_orders": orders,
        "current_margin": round((profit / revenue) * 100, 1) if revenue else 0,
        "average_order_value": round(revenue / orders, 2) if orders else 0,
        "best_month": best["month"],
        "best_month_profit": float(best["profit"] or 0),
        "growth_rate": round(growth, 1),
    }


def category_mix():
    rows = (
        db.session.query(Category.name, func.count(Product.id))
        .outerjoin(Product)
        .group_by(Category.id)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    return [{"category": name, "count": count} for name, count in rows]
