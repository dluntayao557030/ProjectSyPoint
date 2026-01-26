from Utilities.DatabaseConnection import getConnection

class LoginModel:
    """
    Model for Login - provides database connection and query templates.
    Controller handles actual execution.
    """

    @staticmethod
    def getConnection():
        """Returns database connection for controller to use"""
        return getConnection()

    @staticmethod
    def getUserValidationQuery():
        """Returns the query string for user validation"""
        return """
            SELECT user_id, username, password, full_name, role, shift, is_active
            FROM users
            WHERE username = %s AND password = %s AND is_active = TRUE
        """