from app.models.order import Order


def order_profit_snapshot(order: Order):
    return {
        "selling_price": float(order.selling_price or 0),
        "total_cost": order.total_cost,
        "profit": order.profit,
        "margin": round((order.profit / float(order.selling_price)) * 100, 1)
        if float(order.selling_price or 0)
        else 0,
    }
