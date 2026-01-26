"""
AdminProductsModel.py
Model for Admin Product Management operations - Returns queries and parameters
Controller executes the queries
"""


class AdminProductsModel:
    """
    Admin Products model - Provides SQL queries and parameters
    Controllers handle database execution
    """

    # =====================================================
    # CATEGORY QUERIES
    # =====================================================

    @staticmethod
    def get_all_categories_query():
        """
        Get query to fetch all categories
        Returns: (query, params)
        """
        query = """
            SELECT category_id, category_name
            FROM categories
            ORDER BY category_name ASC
        """
        params = ()
        return query, params

    @staticmethod
    def check_category_exists_query(category_name: str):
        """
        Get query to check if category exists
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) 
            FROM categories 
            WHERE category_name = %s
        """
        params = (category_name,)
        return query, params

    @staticmethod
    def create_category_query(category_name: str):
        """
        Get query to create new category
        Returns: (query, params)
        """
        query = """
            INSERT INTO categories (category_name)
            VALUES (%s)
        """
        params = (category_name,)
        return query, params

    # =====================================================
    # PRODUCT QUERIES
    # =====================================================

    @staticmethod
    def get_all_products_query():
        """
        Get query to fetch all products with category info
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active, p.created_at, p.updated_at,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.created_at DESC
        """
        params = ()
        return query, params

    @staticmethod
    def get_filtered_products_query(keyword: str = None, category_id: int = None,
                                    status: str = "All"):
        """
        Get query to fetch filtered products
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active, p.created_at, p.updated_at,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE 1=1
        """
        params = []

        # Keyword filter
        if keyword:
            query += " AND (p.reference_number LIKE %s OR p.product_name LIKE %s)"
            search_term = f"%{keyword}%"
            params.extend([search_term, search_term])

        # Category filter
        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)

        # Status filter
        if status == "Active":
            query += " AND p.is_active = 1"
        elif status == "Archived":
            query += " AND p.is_active = 0"
        # "All" shows both

        query += " ORDER BY p.created_at DESC"

        return query, tuple(params)

    @staticmethod
    def check_reference_exists_query(reference_number: str):
        """
        Get query to check if reference number exists
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) 
            FROM products 
            WHERE reference_number = %s
        """
        params = (reference_number,)
        return query, params

    @staticmethod
    def check_reference_exists_except_query(reference_number: str, product_id: int):
        """
        Get query to check if reference exists except for specific product
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) 
            FROM products 
            WHERE reference_number = %s AND product_id != %s
        """
        params = (reference_number, product_id)
        return query, params

    @staticmethod
    def create_product_query(reference_number: str, product_name: str,
                             price: float, category_id: int):
        """
        Get query to create new product
        Returns: (query, params)
        """
        query = """
            INSERT INTO products 
            (reference_number, product_name, price, category_id, is_active)
            VALUES (%s, %s, %s, %s, 1)
        """
        params = (reference_number, product_name, price, category_id)
        return query, params

    @staticmethod
    def update_product_query(product_id: int, reference_number: str,
                             product_name: str, price: float, category_id: int):
        """
        Get query to update product
        Returns: (query, params)
        """
        query = """
            UPDATE products 
            SET reference_number = %s, product_name = %s, 
                price = %s, category_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """
        params = (reference_number, product_name, price, category_id, product_id)
        return query, params

    @staticmethod
    def archive_product_query(product_id: int):
        """
        Get query to archive product (set is_active = 0)
        Returns: (query, params)
        """
        query = """
            UPDATE products 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """
        params = (product_id,)
        return query, params

    @staticmethod
    def restore_product_query(product_id: int):
        """
        Get query to restore archived product
        Returns: (query, params)
        """
        query = """
            UPDATE products 
            SET is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """
        params = (product_id,)
        return query, params

    @staticmethod
    def get_product_by_id_query(product_id: int):
        """
        Get query to fetch product by ID
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active, p.created_at, p.updated_at,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s
        """
        params = (product_id,)
        return query, params

    @staticmethod
    def get_active_products_query():
        """
        Get query to fetch only active products
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active, p.created_at, p.updated_at,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = 1
            ORDER BY p.product_name ASC
        """
        params = ()
        return query, params

    @staticmethod
    def get_products_by_category_query(category_id: int):
        """
        Get query to fetch products by category
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active, p.created_at, p.updated_at,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.category_id = %s AND p.is_active = 1
            ORDER BY p.product_name ASC
        """
        params = (category_id,)
        return query, params

    @staticmethod
    def get_low_stock_products_query():
        """
        Get query for low stock products
        Note: This assumes a stock/inventory field will be added
        Returns: (query, params)
        """
        query = """
            SELECT 
                p.product_id, p.reference_number, p.product_name, 
                p.price, p.category_id, p.is_active,
                c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = 1
            ORDER BY p.product_name ASC
        """
        params = ()
        return query, params