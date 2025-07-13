import joblib
import pandas as pd

import database as db

model = joblib.load('model/classical_agent_model.pkl')
model_columns = joblib.load('model/model_columns.pkl')


class ClassicalAgent:

    @staticmethod
    def get_classical_block_explanation(username):
        user = db.get_user(username)
        if not user:
            return "User not found.\nप्रयोगकर्ता फेला परेन।"

        _, _, _, _, _, failed_attempts, is_locked = user
        if not is_locked:
            return (
                f"Hello, {username}. Your account is currently active. If you are experiencing issues, please contact "
                f"support.\n"
                f"नमस्कार {username}। तपाईंको खाता हाल सक्रिय छ। यदि तपाईंलाई कुनै समस्या छ भने, कृपया सहायता "
                f"केन्द्रमा सम्पर्क गर्नुहोस्।"
            )

        login_attempts = failed_attempts
        time_since_last_login = 0.5  # dummy value
        ip_address_risk = 'low'  # dummy value
        features = pd.DataFrame(
            [[login_attempts, time_since_last_login, ip_address_risk]],
            columns=['login_attempts', 'time_since_last_login', 'ip_address_risk']
        )
        features = pd.get_dummies(features, columns=['ip_address_risk'], drop_first=True)
        for col in model_columns:
            if col not in features.columns:
                features[col] = 0
        features = features[model_columns]
        prediction = model.predict(features)[0]

        if prediction == 1:
            return (
                f'Hello, {username}. Our system detected unusual activity or too many failed attempts. '
                f'Your account has been temporarily locked for security reasons. Please contact support to unlock it.\n'
                f'नमस्कार {username}। हाम्रो प्रणालीले असामान्य गतिविधि वा धेरै पटक गलत प्रयासहरू पत्ता लगाएको छ। '
                f'तपाईंको खाता सुरक्षाको कारण अस्थायी रूपमा लक गरिएको छ। कृपया खाता अनलक गर्न सहायता केन्द्रमा सम्पर्क गर्नुहोस्।'
            )
        else:
            return (
                f"Hello, {username}. Your account is currently active. If you are experiencing issues, please contact "
                f"support.\n"
                f"नमस्कार {username}। तपाईंको खाता हाल सक्रिय छ। यदि तपाईंलाई कुनै समस्या छ भने, कृपया सहायता "
                f"केन्द्रमा सम्पर्क गर्नुहोस्।"
            )

    @staticmethod
    def validate_recovery_info(username, info_type, info_value):
        user = db.get_user(username)
        if not user:
            return False

        if info_type == "contact":
            return info_value in (user[3], user[4])
        elif info_type == "transaction":
            # In a real system, you'd check transaction history.
            # For this simulation, we'll just accept any numeric input as valid.
            return any(char.isdigit() for char in info_value)

        return False
