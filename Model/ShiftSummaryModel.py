"""
ShiftSummaryModel.py - FIXED
Model for Shift Summary operations - Returns queries and parameters
FIXED: Queries now use today's start time (midnight) instead of shift-specific times
This ensures all cashiers see their transactions from today regardless of their assigned shift
"""
from datetime import datetime


class ShiftSummaryModel:
    """
    Shift Summary model - Provides SQL queries and parameters
    Controllers handle database execution

    FIXED: All queries now filter by cashier_id and transactions from today (midnight onwards)
    """

    @staticmethod
    def get_total_sales_query(cashier_id: int, today_start: datetime):
        """
        Get query for total sales from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT COALESCE(SUM(final_total), 0) as total_sales
            FROM transactions
            WHERE cashier_id = %s
              AND status = 'completed'
              AND transaction_date >= %s
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_items_sold_query(cashier_id: int, today_start: datetime):
        """
        Get query for items sold from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT COALESCE(SUM(ti.quantity), 0) as items_sold
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE t.cashier_id = %s
              AND t.status = 'completed'
              AND t.transaction_date >= %s
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_transaction_count_query(cashier_id: int, today_start: datetime):
        """
        Get query for transaction count from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT COUNT(*) as transaction_count
            FROM transactions
            WHERE cashier_id = %s
              AND status = 'completed'
              AND transaction_date >= %s
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_payment_breakdown_query(cashier_id: int, today_start: datetime):
        """
        Get query for payment methods breakdown from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        Note: Since we don't have a separate payments table yet,
        we'll return a placeholder query. Update when payments table is added.
        """
        query = """
            SELECT 
                'Cash' as payment_method,
                COUNT(*) as count,
                SUM(final_total) as total
            FROM transactions
            WHERE cashier_id = %s
              AND status = 'completed'
              AND transaction_date >= %s
            UNION ALL
            SELECT 
                'GCash' as payment_method,
                0 as count,
                0 as total
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_top_products_query(cashier_id: int, today_start: datetime):
        """
        Get query for top 5 products sold from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT 
                ti.product_name,
                SUM(ti.quantity) as total_qty
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE t.cashier_id = %s
              AND t.status = 'completed'
              AND t.transaction_date >= %s
            GROUP BY ti.product_id, ti.product_name
            ORDER BY total_qty DESC
            LIMIT 5
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_shift_transactions_query(cashier_id: int, today_start: datetime):
        """
        Get query for all transactions from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT 
                t.transaction_number,
                t.transaction_date,
                COUNT(ti.transaction_item_id) as items_count,
                t.final_total,
                dt.type_name as discount_type
            FROM transactions t
            LEFT JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            LEFT JOIN discount_types dt ON t.discount_type_id = dt.discount_type_id
            WHERE t.cashier_id = %s
              AND t.status = 'completed'
              AND t.transaction_date >= %s
            GROUP BY t.transaction_id
            ORDER BY t.transaction_date DESC
        """
        params = (cashier_id, today_start)
        return query, params

    @staticmethod
    def get_hourly_sales_query(cashier_id: int, today_start: datetime):
        """
        Get query for hourly sales breakdown (for charts) from today
        Returns: (query, params)

        FIXED: Uses today_start (midnight) instead of shift_start
        """
        query = """
            SELECT 
                HOUR(transaction_date) as hour,
                COUNT(*) as transaction_count,
                SUM(final_total) as total_sales
            FROM transactions
            WHERE cashier_id = %s
              AND status = 'completed'
              AND transaction_date >= %s
            GROUP BY HOUR(transaction_date)
            ORDER BY hour
        """
        params = (cashier_id, today_start)
        return query, params