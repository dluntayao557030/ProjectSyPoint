"""
TransactionModel.py
Model for Transaction operations - Returns queries and parameters
Controller executes the queries
"""

class TransactionModel:
    """
    Transaction model - Provides SQL queries and parameters
    Controllers handle database execution
    """

    @staticmethod
    def get_product_query(reference_number: str):
        """
        Get query to fetch product by reference number
        Returns: (query, params)
        """
        query = """
            SELECT product_id, reference_number, product_name, price
            FROM products
            WHERE reference_number = %s AND is_active = TRUE
        """
        params = (reference_number.upper(),)
        return query, params

    @staticmethod
    def verify_admin_code_query(admin_code: str):
        """
        Get query to verify admin code
        Returns: (query, params)
        """
        query = """
            SELECT user_id, username, full_name, role
            FROM users
            WHERE password = %s AND role = 'admin' AND is_active = TRUE
        """
        params = (admin_code,)
        return query, params

    @staticmethod
    def get_discount_type_id_query(discount_type_name: str):
        """
        Get query to fetch discount type ID
        Returns: (query, params)
        """
        # Extract discount type name (e.g., "Senior Citizen (20%)" -> "Senior Citizen")
        type_name = discount_type_name.split('(')[0].strip()

        query = """
            SELECT discount_type_id
            FROM discount_types
            WHERE type_name = %s
        """
        params = (type_name,)
        return query, params

    @staticmethod
    def create_transaction_query(transaction_number: str, cashier_id: int,
                                 subtotal: float, discount_amount: float,
                                 final_total: float, discount_type_id: int = None):
        """
        Get query to create new transaction
        Returns: (query, params)
        """
        query = """
            INSERT INTO transactions 
            (transaction_number, cashier_id, transaction_date, subtotal, 
             discount_amount, final_total, discount_type_id, status)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, 'completed')
        """
        params = (transaction_number, cashier_id, subtotal, discount_amount,
                  final_total, discount_type_id)
        return query, params

    @staticmethod
    def add_transaction_item_query(transaction_id: int, product_id: int,
                                   product_name: str, quantity: int,
                                   unit_price: float, total_price: float):
        """
        Get query to add transaction item
        Returns: (query, params)
        """
        query = """
            INSERT INTO transaction_items
            (transaction_id, product_id, product_name, quantity, 
             unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (transaction_id, product_id, product_name, quantity,
                  unit_price, total_price)
        return query, params

    @staticmethod
    def get_todays_sales_query(cashier_id: int):
        """
        Get query for today's total sales
        Returns: (query, params)
        """
        query = """
            SELECT COALESCE(SUM(final_total), 0) as total_sales
            FROM transactions
            WHERE cashier_id = %s
              AND status = 'completed'
              AND DATE(transaction_date) = CURDATE()
        """
        params = (cashier_id,)
        return query, params

    @staticmethod
    def get_todays_items_query(cashier_id: int):
        """
        Get query for today's items sold
        Returns: (query, params)
        """
        query = """
            SELECT COALESCE(SUM(ti.quantity), 0) as items_sold
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE t.cashier_id = %s
              AND t.status = 'completed'
              AND DATE(t.transaction_date) = CURDATE()
        """
        params = (cashier_id,)
        return query, params

    @staticmethod
    def get_todays_transactions_query(cashier_id: int):
        """
        Get query for today's transactions list
        Returns: (query, params)
        """
        query = """
            SELECT 
                t.transaction_number,
                t.transaction_date,
                COUNT(ti.transaction_item_id) as items_count,
                t.final_total,
                u.full_name as cashier_name
            FROM transactions t
            LEFT JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            JOIN users u ON t.cashier_id = u.user_id
            WHERE t.cashier_id = %s
              AND t.status = 'completed'
              AND DATE(t.transaction_date) = CURDATE()
            GROUP BY t.transaction_id
            ORDER BY t.transaction_date DESC
        """
        params = (cashier_id,)
        return query, params