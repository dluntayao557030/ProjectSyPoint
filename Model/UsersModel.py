"""
AdminUsersModel.py
Model for Admin User Management operations - Returns queries and parameters
Controller executes the queries
"""


class AdminUsersModel:
    """
    Admin Users model - Provides SQL queries and parameters
    Controllers handle database execution
    """

    @staticmethod
    def get_all_users_query():
        """
        Get query to fetch all users
        Returns: (query, params)
        """
        query = """
            SELECT 
                user_id, username, full_name, role, shift, is_active,
                created_at, updated_at
            FROM users
            ORDER BY created_at DESC
        """
        params = ()
        return query, params

    @staticmethod
    def search_users_query(keyword: str):
        """
        Get query to search users
        Returns: (query, params)
        """
        query = """
            SELECT 
                user_id, username, full_name, role, shift, is_active,
                created_at, updated_at
            FROM users
            WHERE username LIKE %s 
               OR full_name LIKE %s 
               OR role LIKE %s
            ORDER BY created_at DESC
        """
        search_term = f"%{keyword}%"
        params = (search_term, search_term, search_term)
        return query, params

    @staticmethod
    def check_username_exists_query(username: str):
        """
        Get query to check if username exists
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) 
            FROM users 
            WHERE username = %s
        """
        params = (username,)
        return query, params

    @staticmethod
    def check_username_exists_except_query(username: str, user_id: int):
        """
        Get query to check if username exists except for specific user
        Returns: (query, params)
        """
        query = """
            SELECT COUNT(*) 
            FROM users 
            WHERE username = %s AND user_id != %s
        """
        params = (username, user_id)
        return query, params

    @staticmethod
    def create_user_query(username: str, password: str, full_name: str,
                          role: str, shift: str):
        """
        Get query to create new user
        Returns: (query, params)
        """
        query = """
            INSERT INTO users 
            (username, password, full_name, role, shift, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """
        params = (username, password, full_name, role, shift)
        return query, params

    @staticmethod
    def update_user_query(user_id: int, username: str, password: str,
                          full_name: str, role: str, shift: str, is_active: int):
        """
        Get query to update user
        If password is None, don't update it
        Returns: (query, params)
        """
        if password:
            query = """
                UPDATE users 
                SET username = %s, password = %s, full_name = %s, 
                    role = %s, shift = %s, is_active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """
            params = (username, password, full_name, role, shift, is_active, user_id)
        else:
            query = """
                UPDATE users 
                SET username = %s, full_name = %s, role = %s, 
                    shift = %s, is_active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """
            params = (username, full_name, role, shift, is_active, user_id)

        return query, params

    @staticmethod
    def get_user_by_id_query(user_id: int):
        """
        Get query to fetch user by ID
        Returns: (query, params)
        """
        query = """
            SELECT 
                user_id, username, full_name, role, shift, is_active,
                created_at, updated_at
            FROM users
            WHERE user_id = %s
        """
        params = (user_id,)
        return query, params

    @staticmethod
    def get_active_users_query():
        """
        Get query to fetch only active users
        Returns: (query, params)
        """
        query = """
            SELECT 
                user_id, username, full_name, role, shift, is_active,
                created_at, updated_at
            FROM users
            WHERE is_active = 1
            ORDER BY full_name ASC
        """
        params = ()
        return query, params

    @staticmethod
    def get_users_by_role_query(role: str):
        """
        Get query to fetch users by role
        Returns: (query, params)
        """
        query = """
            SELECT 
                user_id, username, full_name, role, shift, is_active,
                created_at, updated_at
            FROM users
            WHERE role = %s AND is_active = 1
            ORDER BY full_name ASC
        """
        params = (role,)
        return query, params