import sqlite3
import datetime
import json

from flask import Flask
from flask import g

DATABASE = './sales.db'

app = Flask(__name__)


def get_db():
    """Get database connection.
    """

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection.
    """

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Query the database.

    Args:
        query (str): SQLite query
        args (tuple, optional): Query arguments. Defaults to ().
        one (bool, optional): Single or multiple results requested. Defaults to False.

    Returns:
        variable: Results of the query.
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()

    return (rv[0] if rv else None) if one else rv


def query_summary(date):
    """Query a sales summary for a particular date. Checks that the
    given date is valid. Dates may be valid but not contained within
    the database, in which case 0 is returned for all values.

    Args:
        date (str): Date in format 'YYYY-MM-DD' format

    Returns:
        str: Summary as a JSON string, or "Invalid date"
    """

    try:
        from_date, to_date = validate_date(date)
    except ValueError:
        return "Invalid date"

    # TODO round to 2 d.p.
    result = {}
    result['items'] = query_total_items_by_date(from_date, to_date)
    result['customers'] = query_total_customers_by_date(from_date, to_date)
    result['total_discount_amount'] = query_total_discount_by_date(from_date, to_date)
    result['discount_rate_avg'] = query_average_discount_rate_by_date(from_date, to_date)
    result['order_total_avg'] = query_average_order_total_by_date(from_date, to_date)
    result['commissions'] = {}
    result['commissions']['total'] = query_total_commissions_by_date(from_date, to_date)
    result['commissions']['order_average'] = query_average_order_commission_by_date(from_date, to_date)

    return json.dumps(result, indent=4)


def query_total_items_by_date(from_date, to_date):
    """Query the database for the total number of items sold on a given date.

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        int: this will be 0 if the date is valid but outside the range held in the database.
    """

    query = f"""
        SELECT SUM(order_lines.quantity) 
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}' """
    
    # result is a 1-tuple
    result = query_db(query, one=True)

    return 0 if not result[0] else result[0]


def query_total_customers_by_date(from_date, to_date):
    """Query the database for the total number of customers submitting orders on a given date.

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        int: this will be 0 if the date is valid but outside the range held in the database.
    """
    
    query = f"""
        SELECT DISTINCT orders.customer_id
        FROM orders
        WHERE created_at BETWEEN '{from_date}' AND '{to_date}' """
    
    # result is a list of 1-tuples
    result = query_db(query)

    return len(result)


def query_total_discount_by_date(from_date, to_date):
    """Query the database for the total discount given on a given date.
    
    It is assumed that the discount is the 'full_price_amoumnt' minus the 'discounted_amount'

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        float: this will be 0.0 if the date is valid but outside the range held in the database.
    """
    query = f"""
        SELECT SUM(order_lines.full_price_amount), SUM(order_lines.discounted_amount) 
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}' """
        
    # result is a 2-tuple
    result = query_db(query, one=True)

    return 0.0 if not result[0] else result[0] - result[1]


def query_average_discount_rate_by_date(from_date, to_date):
    """Query the database for the average discount given on a given date.
    
    The average is calculated for non-zero discount rates.

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        float: this will be 0.0 if the date is valid but outside the range held in the database.
    """
    
    query = f"""
        SELECT order_lines.discount_rate
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}' """
    
    # result is a list of 1-tuples
    result = query_db(query)

    # only choose non-zero rates
    result = [r[0] for r in result if r[0] > 0.0]
    
    return 0.0 if len(result) == 0 else sum(result)/len(result)


def query_average_order_total_by_date(from_date, to_date):
    """Query the database for the average order total given on a given date.
    
    The average is calculated over the total amount for each individual order.

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        float: this will be 0.0 if the date is valid but outside the range held in the database.
    """
    
    query = f"""
        SELECT SUM(order_lines.total_amount)
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY orders.id"""
        
    # result is a list of 1-tuples
    result = query_db(query)
    
    # only need first part of tuple
    result = [r[0] for r in result]
    
    return 0.0 if len(result) == 0 else sum(result)/len(result)


def query_total_commissions_by_date(from_date, to_date):
    """Get total commissions by date.

    This assumes that this is the total for an order multiplied by the rate for that
    vendor on that date.    

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        float: this will be 0.0 if the date is valid but outside the range held in the database.
    """
    
    # get rates by date
    query = f"""
        SELECT vendor_id, rate
        FROM commissions
        WHERE date BETWEEN '{from_date}' AND '{to_date}' """

    # result is a list of 2-tuples
    result = query_db(query)
    rates = {i[0]: i[1] for i in result}
    
    query = f"""
        SELECT order_lines.total_amount, orders.vendor_id
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY orders.vendor_id
        """
    
    # result is a list of 2-tuples
    result = query_db(query)
    vendors = {i[1]: i[0] for i in result}

    if rates and vendors:
        return sum([v * rates.get(k, '0.0') for k, v in vendors.items()])

    return 0.0


def query_average_order_commission_by_date(from_date, to_date):
    """Get average order commission by date.

    Args:
        from_date (str): Date in format 'YYYY-MM-DD' format
        to_date (str):Date in format 'YYYY-MM-DD' format

    Returns:
        float: this will be 0.0 if the date is valid but outside the range held in the database.
    """

    # get rates by date
    query = f"""
        SELECT vendor_id, rate
        FROM commissions
        WHERE date BETWEEN '{from_date}' AND '{to_date}' """

    # result is a list of 2-tuples
    result = query_db(query)
    rates = {i[0]: i[1] for i in result}

    # get average orders
    query = f"""
        SELECT SUM(order_lines.total_amount), orders.vendor_id
        FROM order_lines INNER JOIN orders ON orders.id = order_lines.order_id
        WHERE orders.created_at BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY orders.id
        """
    
    # result is a list of 2-tuples: order total, vendor ID        
    orders = query_db(query)
    
    if len(orders) > 0:
        return sum([t * rates[v] for t,v in orders])/len(orders) 

    return 0.0

def validate_date(date):
    """Validate a given date and return the appropriate 'from' and 'to' dates.
    
    For example, given the date '2019-08-01' this function will check that it is
    a valid date and if so return the bracketed dates for the SQL query. In this
    case the 'from' date is '2019-08-01' and the 'to' date is '2019-08-02'.
    
    Raises a ValueError if a date is invalid.

    Args:
        date (str): The date (day) to query, in 'YYYY-MM-DD' format.
        
    Returns:
        str, str: The 'from' date and the 'to' date.
    """

    to_date = datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=1)

    return date, to_date.strftime('%Y-%m-%d')
