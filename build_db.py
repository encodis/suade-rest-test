import os
import sys
import csv
import argparse
import sqlite3


def create_tables(db_path):
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    # create orders table
    curs.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            created_at TEXT,
            vendor_id INTEGER,
            customer_id INTEGER
        );
        """)
        
    # create order_lines table
    curs.execute("""
        CREATE TABLE IF NOT EXISTS order_lines (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_description TEXT,
            product_price INTEGER,
            product_vat_rate REAL,
            discount_rate REAL,
            quantity INTEGER,
            full_price_amount REAL,
            discounted_amount REAL,
            vat_amount REAL,
            total_amount REAL,
            FOREIGN KEY (order_id)
                REFERENCES orders(id)
        );
        """)
    
    curs.execute("""
        CREATE TABLE IF NOT EXISTS commissions (
            date TEXT,
            vendor_id INTEGER,
            rate REAL
        );
        """)
    
    curs.execute("""
        CREATE TABLE IF NOT EXISTS product_promo (
            date TEXT,
        product_id INTEGER,
        promotion_id INTEGER
        );
        """)
    
    conn.commit()
    conn.close()

def populate_tables(db_path, data_dir):
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()
    
    # populate orders table
    with open(os.path.join(data_dir, 'orders.csv'), 'r') as f:
        dr = csv.DictReader(f)
        rows = [(i['id'], i['created_at'], i['vendor_id'], i['customer_id']) for i in dr]

    curs.executemany("INSERT INTO orders (id, created_at, vendor_id, customer_id) VALUES (?, ?, ?, ?);", rows)
    
    # populate order_lines table
    with open(os.path.join(data_dir, 'order_lines.csv'), 'r') as f:
        dr = csv.DictReader(f)
        rows = [(i['order_id'], i['product_id'], i['product_description'], i['product_price'], i['product_vat_rate'], i['discount_rate'], i['quantity'], i['full_price_amount'], i['discounted_amount'], i['vat_amount'], i['total_amount']) for i in dr]

    curs.executemany("INSERT INTO order_lines (order_id, product_id, product_description, product_price, product_vat_rate, discount_rate, quantity, full_price_amount, discounted_amount, vat_amount, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", rows)    
    
    # populate commissions table
    with open(os.path.join(data_dir, 'commissions.csv'), 'r') as f:
        dr = csv.DictReader(f)
        rows = [(i['date'], i['vendor_id'], i['rate']) for i in dr]
    
    curs.executemany("INSERT INTO commissions (date, vendor_id, rate) VALUES (?, ?, ?);", rows)
    
    # populate product promotions table
    with open(os.path.join(data_dir, 'product_promotions.csv'), 'r') as f:
        dr = csv.DictReader(f)
        rows = [(i['date'], i['product_id'], i['promotion_id']) for i in dr]
    
    curs.executemany("INSERT INTO product_promo (date, product_id, promotion_id) VALUES (?, ?, ?);", rows)

    # finalise
    conn.commit()
    conn.close()


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Build sample database')

    parser.add_argument('data_dir', help='Folder containing CSVs')
    parser.add_argument('db_path', help='Path to database')
    parser.add_argument("--rebuild", default=False, help='Delete and rebuild database', action='store_true')

    args = parser.parse_args(args)

    if os.path.exists(args.db_path):
        if args.rebuild:
            os.remove(args.db_path)
        else:
            print('Database already exists.')
            return

    create_tables(args.db_path)
    populate_tables(args.db_path, args.data_dir)

    print('Database ready.')


# execute if main
if __name__ == '__main__':
    main()
