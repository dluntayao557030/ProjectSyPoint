"""
AdminReportsModel.py
Model for Admin Reports operations - Returns queries and parameters
Controller executes the queries
"""
from datetime import date


class AdminReportsModel:
    """
    Admin Reports model - Provides SQL queries and parameters
    Controllers handle database execution
    """

    @staticmethod
    def get_daily_sales_report_query(from_date: date, to_date: date):
        """
        Get query for Daily Sales Report
        Shows total sales, transactions, discounts per day
        Returns: (query, params)
        """
        query = """
            SELECT 
                DATE(transaction_date) as sale_date,
                COUNT(*) as transaction_count,
                SUM(subtotal + (subtotal * 0.12)) as gross_sales,
                COALESCE(SUM(discount_amount), 0) as total_discounts,
                SUM(final_total) as net_sales
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN %s AND %s
              AND status = 'completed'
            GROUP BY DATE(transaction_date)
            ORDER BY sale_date DESC
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_shift_summary_report_query(from_date: date, to_date: date):
        """
        Get query for Shift Summary Report
        Shows performance per cashier shift
        Returns: (query, params)
        """
        query = """
            SELECT 
                DATE(t.transaction_date) as shift_date,
                u.full_name as cashier_name,
                u.shift,
                COUNT(*) as transaction_count,
                SUM(t.final_total) as total_sales,
                COALESCE(SUM(t.discount_amount), 0) as total_discounts
            FROM transactions t
            JOIN users u ON t.cashier_id = u.user_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY DATE(t.transaction_date), t.cashier_id, u.full_name, u.shift
            ORDER BY shift_date DESC, cashier_name
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_cashier_performance_report_query(from_date: date, to_date: date):
        """
        Get query for Cashier Performance Report
        Shows individual cashier performance metrics
        Returns: (query, params)
        """
        query = """
            SELECT 
                u.full_name as cashier_name,
                COUNT(*) as transaction_count,
                SUM(t.final_total) as total_sales,
                AVG(t.final_total) as avg_transaction
            FROM transactions t
            JOIN users u ON t.cashier_id = u.user_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY t.cashier_id, u.full_name
            ORDER BY total_sales DESC
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_product_sales_report_query(from_date: date, to_date: date):
        """
        Get query for Product Sales Report
        Shows product performance by sales volume and revenue
        Returns: (query, params)
        """
        query = """
            SELECT 
                ti.product_name,
                c.category_name,
                SUM(ti.quantity) as quantity_sold,
                SUM(ti.total_price) as revenue,
                AVG(ti.unit_price) as avg_price
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            JOIN products p ON ti.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY ti.product_id, ti.product_name, c.category_name
            ORDER BY revenue DESC
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_discount_usage_report_query(from_date: date, to_date: date):
        """
        Get query for Discount Usage Report
        Tracks discount application by type
        Returns: (query, params)
        """
        query = """
            SELECT 
                COALESCE(dt.type_name, 'None') as discount_type,
                COUNT(*) as usage_count,
                COALESCE(SUM(t.discount_amount), 0) as total_discount_amount,
                COALESCE(AVG(t.discount_amount), 0) as avg_discount
            FROM transactions t
            LEFT JOIN discount_types dt ON t.discount_type_id = dt.discount_type_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY t.discount_type_id, dt.type_name
            ORDER BY total_discount_amount DESC
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_top_selling_products_query(from_date: date, to_date: date, limit: int = 10):
        """
        Get query for top selling products
        Returns: (query, params)
        """
        query = """
            SELECT 
                ti.product_name,
                SUM(ti.quantity) as total_quantity,
                SUM(ti.total_price) as total_revenue
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY ti.product_id, ti.product_name
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        params = (from_date, to_date, limit)
        return query, params

    @staticmethod
    def get_category_performance_query(from_date: date, to_date: date):
        """
        Get query for category performance
        Returns: (query, params)
        """
        query = """
            SELECT 
                c.category_name,
                COUNT(DISTINCT ti.product_id) as product_count,
                SUM(ti.quantity) as items_sold,
                SUM(ti.total_price) as revenue
            FROM transaction_items ti
            JOIN transactions t ON ti.transaction_id = t.transaction_id
            JOIN products p ON ti.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE DATE(t.transaction_date) BETWEEN %s AND %s
              AND t.status = 'completed'
            GROUP BY c.category_id, c.category_name
            ORDER BY revenue DESC
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_hourly_sales_distribution_query(from_date: date, to_date: date):
        """
        Get query for hourly sales distribution
        Returns: (query, params)
        """
        query = """
            SELECT 
                HOUR(transaction_date) as hour,
                COUNT(*) as transaction_count,
                SUM(final_total) as total_sales
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN %s AND %s
              AND status = 'completed'
            GROUP BY HOUR(transaction_date)
            ORDER BY hour
        """
        params = (from_date, to_date)
        return query, params

    @staticmethod
    def get_payment_method_breakdown_query(from_date: date, to_date: date):
        """
        Get query for payment method breakdown
        Note: Placeholder since payment methods aren't stored separately yet
        Returns: (query, params)
        """
        query = """
            SELECT 
                'Cash' as payment_method,
                COUNT(*) as transaction_count,
                SUM(final_total) as total_amount
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN %s AND %s
              AND status = 'completed'
        """
        params = (from_date, to_date)
        return query, params