import database as db


class AuthService:

    @staticmethod
    def login_or_register(username, password, email, phone, action):
        if action == "Register":
            if not email or not phone:
                return "Email and phone are required for registration."
            if db.create_user(username, password, email, phone):
                return "Registration successful! You can now log in."
            else:
                return "Username already exists."
        elif action == "Login":
            user = db.get_user(username)
            if not user:
                return "User not found."

            _, _, _, _, _, failed_attempts, is_locked = user
            if is_locked:
                return "ACCOUNT_LOCKED"

            if user[2] == password:
                db.update_user(username, 0, 0)
                return f"Welcome, {username}!"
            else:
                failed_attempts += 1
                if failed_attempts >= 3:
                    db.update_user(username, failed_attempts, 1)
                    return "Too many failed login attempts. Your account is now locked."
                else:
                    db.update_user(username, failed_attempts, 0)
                    return f"Invalid password. You have {3 - failed_attempts} attempts remaining."

    @staticmethod
    def unlock_account(username):
        db.update_user(username, 0, 0)
        return f"Account for {username} has been unlocked."

    @staticmethod
    def update_password(username, new_password):
        db.update_user_password(username, new_password)
        return "Password updated successfully."

    @staticmethod
    def check_account_status(username):
        user = db.get_user(username)
        if not user:
            return "not_found"
        _, _, _, _, _, failed_attempts, is_locked = user
        if is_locked:
            return "locked"
        else:
            return "active"
