"""
AdminDashboardModel.py
Model for Admin Dashboard operations - Returns queries and parameters
Controller executes the queries
"""
from datetime import date


class AdminDashboardModel:
    """
    Admin Dashboard model - Provides SQL queries and parameters
    Controllers handle database execution
    """

    @staticmethod
    def get_total_sales_today_query(today: date):
        """
        Get query for total sales today
        Returns: (query, params)
        """
        query = """
            SELECT COALESCE(SUM(final_total), 0) as total_sales
            FROM transactions
            WHERE DATE(transaction_date) = %s
              AND status = 'completed'
        """
        params = (today,)
        return query, params

    @staticmethod
    def get_transactions_today_query(today: date):
        """
        Get query for transaction count today
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) as transaction_count
            FROM transactions
            WHERE DATE(transaction_date) = %s
              AND status = 'completed'
        """
        params = (today,)
        return query, params

    @staticmethod
    def get_products_sold_today_query(today: date):
        """
        Get query for products sold today
        Returns: (query, params)
        """
        query = """
            SELECT COALESCE(SUM(ti.quantity), 0) as products_sold
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE DATE(t.transaction_date) = %s
              AND t.status = 'completed'
        """
        params = (today,)
        return query, params

    @staticmethod
    def get_sales_by_date_query(start_date: date, end_date: date):
        """
        Get query for sales grouped by date
        Returns: (query, params)
        """
        query = """
            SELECT 
                DATE(transaction_date) as sale_date,
                COALESCE(SUM(final_total), 0) as total_sales
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN %s AND %s
              AND status = 'completed'
            GROUP BY DATE(transaction_date)
            ORDER BY sale_date ASC
        """
        params = (start_date, end_date)
        return query, params

    @staticmethod
    def get_sales_detail_query(today: date):
        """
        Get query for detailed sales today (no IDs exposed)
        Returns: (query, params)
        """
        query = """
            SELECT 
                t.transaction_number,
                t.transaction_date,
                u.full_name as cashier_name,
                t.subtotal,
                t.discount_amount,
                t.final_total
            FROM transactions t
            JOIN users u ON t.cashier_id = u.user_id
            WHERE DATE(t.transaction_date) = %s
              AND t.status = 'completed'
            ORDER BY t.transaction_date DESC
        """
        params = (today,)
        return query, params

    @staticmethod
    def get_transactions_detail_query(today: date):
        """
        Get query for detailed transactions today (no IDs exposed)
        Returns: (query, params)
        """
        query = """
            SELECT 
                t.transaction_number,
                t.transaction_date,
                u.full_name as cashier_name,
                COUNT(ti.transaction_item_id) as items_count,
                t.final_total
            FROM transactions t
            JOIN users u ON t.cashier_id = u.user_id
            LEFT JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            WHERE DATE(t.transaction_date) = %s
              AND t.status = 'completed'
            GROUP BY t.transaction_id
            ORDER BY t.transaction_date DESC
        """
        params = (today,)
        return query, params

    @staticmethod
    def get_products_detail_query(today: date):
        """
        Get query for products sold today with details (no IDs exposed)
        Returns: (query, params)
        """
        query = """
            SELECT 
                ti.product_name,
                SUM(ti.quantity) as quantity_sold,
                SUM(ti.total_price) as revenue
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE DATE(t.transaction_date) = %s
              AND t.status = 'completed'
            GROUP BY ti.product_name
            ORDER BY revenue DESC
        """
        params = (today,)
        return query, params