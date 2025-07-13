import pandas as pd
import numpy as np

num_samples = 1000
data = {
    'login_attempts': np.random.randint(1, 10, size=num_samples),
    'time_since_last_login': np.random.uniform(0, 72, size=num_samples),
    'ip_address_risk': np.random.choice(['low', 'medium', 'high'], size=num_samples, p=[0.7, 0.2, 0.1])
}
df = pd.DataFrame(data)

conditions = [
    (df['login_attempts'] >= 5),
    (df['login_attempts'] >= 3) & (df['time_since_last_login'] < 1),
    (df['ip_address_risk'] == 'high')
]

df['is_locked'] = np.where(np.logical_or.reduce(conditions), 1, 0)

df.to_csv('login_attempts.csv', index=False)
