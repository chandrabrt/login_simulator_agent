# AgentSync Login Simulator

## Project Overview

The AgentSync Login Simulator is a Streamlit-based web application designed to demonstrate and compare different approaches to user authentication, account security, and recovery using both traditional "Classical Agents" (machine learning models) and "Generative AI Agents" (Google's Gemini API).

This simulator provides a hands-on experience for:
*   **User Authentication:** Login and registration functionalities.
*   **Account Security:** Simulating account locking due to failed login attempts.
*   **Account Lock Analysis:** Explaining why an account was locked using either a classical ML model or a GenAI model.
*   **Account Recovery:** A multi-step recovery process guided by either a classical agent or a GenAI agent.

## Features

*   **User Management:** Register new users and log in existing ones.
*   **Account Locking:** Accounts are automatically locked after a configurable number of failed login attempts.
*   **Dual Agent System:**
    *   **Classical Agent:** Utilizes a pre-trained machine learning model (e.g., Logistic Regression) to analyze login patterns and provide explanations for account locks, and to validate recovery information.
    *   **GenAI Agent:** Leverages the Google Gemini API to provide more conversational and context-aware explanations for account locks and guide users through the recovery process.
*   **Interactive UI:** Built with Streamlit for an intuitive user experience.
*   **SQLite Database:** Simple database for user storage.

## Project Structure

```
.
├── auth_service.py           # Handles core authentication logic (login, registration, password updates, account status checks).
├── classical_agent.py        # Implements the Classical Agent for account lock analysis and recovery info validation.
├── database.py               # Manages SQLite database interactions (user creation, retrieval, updates).
├── data/
│   └── login_attempts.csv    # Dummy data for training the classical agent.
├── flow_diagram.png          # (Assumed) Visual representation of the system's flow.
├── gen_ai_agent.py           # Implements the GenAI Agent for account lock explanations.
├── login_security.db         # SQLite database file (generated upon first run).
├── login_simulator.py        # Core simulation logic, integrating authentication and agent functionalities.
├── main.py                   # The main Streamlit application file, defining the UI and orchestrating interactions.
├── medium_article.md         # (Assumed) Markdown file for a related Medium article.
├── model/
│   ├── classical_agent_model.pkl # Pre-trained classical machine learning model.
│   ├── model_columns.pkl     # List of columns used by the classical model during training.
│   ├── model_generator.py    # Script to generate synthetic data for model training.
│   └── train_model.py        # Script to train and save the classical agent model.
├── README.md                 # This file.
└── requirements.txt          # Python dependencies required to run the project.
```

### File Breakdown:

*   **`auth_service.py`**:
    *   `AuthService` class: Provides static methods for user authentication (`login_or_register`), validating recovery information (`validate_recovery_info`), unlocking accounts (`unlock_account`), updating passwords (`update_password`), and checking account status (`check_account_status`). It interacts directly with `database.py`.

*   **`classical_agent.py`**:
    *   `ClassicalAgent` class: Contains methods for the classical machine learning agent.
    *   `get_classical_block_explanation`: Uses a loaded `classical_agent_model.pkl` to predict and explain why an account might be locked based on simulated features like login attempts, time since last login, and IP address risk.
    *   `validate_recovery_info`: Validates user recovery information (contact or transaction details) against stored user data.

*   **`database.py`**:
    *   Handles all interactions with the `login_security.db` SQLite database.
    *   `init_db()`: Initializes the database and creates the `users` table if it doesn't exist.
    *   `create_user()`: Adds a new user to the database.
    *   `get_user()`: Retrieves user details by username.
    *   `update_user()`: Updates user login attempts and lock status.
    *   `update_user_password()`: Updates a user's password.

*   **`data/login_attempts.csv`**:
    *   A CSV file containing synthetic data used to train the `classical_agent_model.pkl`. It likely includes features like `login_attempts`, `time_since_last_login`, `ip_address_risk`, and a target variable indicating whether an account should be locked.

*   **`gen_ai_agent.py`**:
    *   `GenAIAgent` class: Implements the Generative AI agent.
    *   `get_genai_block_explanation`: Uses the Google Gemini API to generate a natural language explanation for an account lock, providing a more user-friendly response than the classical agent.

*   **`login_simulator.py`**:
    *   `LoginSimulator` class: Acts as an orchestrator for the simulation.
    *   `start_genai_recovery_chat`: Initiates a recovery conversation with the GenAI model, tailoring the prompt based on account status.
    *   `get_block_explanation`: A dispatcher method that calls either the Classical Agent or GenAI Agent for lock explanations based on the selected agent type.
    *   `genai_chat_response`: Manages the multi-step recovery flow, validating user input at each step using either `AuthService` or `ClassicalAgent` based on the selected agent type, and generating responses via the GenAI model.

*   **`main.py`**:
    *   The Streamlit application's entry point.
    *   Sets up the Streamlit page configuration and custom CSS for styling.
    *   Initializes session state variables for managing UI state (login status, chat history, recovery state).
    *   Defines the three main tabs: "Access Portal" (Login/Register), "Lock Insights" (Account Lock Analysis), and "Recovery Assistant" (AI-Powered Recovery).
    *   Handles user input and button clicks, calling appropriate functions from `AuthService` and `LoginSimulator`.
    *   Displays messages and chat history dynamically.

*   **`model/`**:
    *   **`classical_agent_model.pkl`**: A serialized Python object (pickle file) containing the trained machine learning model used by `classical_agent.py`.
    *   **`model_columns.pkl`**: A serialized list of column names that the `classical_agent_model.pkl` expects as input features. This ensures consistency between training and prediction.
    *   **`model_generator.py`**: A script responsible for generating the synthetic `login_attempts.csv` data. This is crucial for creating a dataset to train the classical agent.
    *   **`train_model.py`**: A script that loads the `login_attempts.csv` data, preprocesses it, trains a machine learning model (e.g., Logistic Regression), and then saves the trained model and its feature columns to `classical_agent_model.pkl` and `model_columns.pkl` respectively.

*   **`requirements.txt`**:
    *   Lists all Python packages required to run the project, including `streamlit`, `scikit-learn`, `pandas`, `google-generativeai`, etc.

## Setup and Installation

To set up and run the AgentSync Login Simulator locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AgentSync-Login-Simulator.git
    cd AgentSync-Login-Simulator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows:**
        ```bash
        .venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Google Gemini API Key:**
    *   Obtain a Google Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a `.env` file in the root directory of the project and add your API key:
        ```
        GEMINI_API_KEY='YOUR_GEMINI_API_KEY'
        ```
    *   Alternatively, you can set it as an environment variable in your system.

6.  **Generate and Train the Classical Model (if not already present):**
    *   The project includes pre-trained models, but you can regenerate them if needed.
    ```bash
    python model/model_generator.py
    python model/train_model.py
    ```
    This will create `login_attempts.csv` in the `data/` directory and `classical_agent_model.pkl` and `model_columns.pkl` in the `model/` directory.

7.  **Run the Streamlit application:**
    ```bash
    streamlit run main.py
    ```

    This will open the application in your web browser.

## Usage

Once the application is running, you can interact with it through the following tabs:

### 1. Access Portal

*   **Login:** Enter a username and password to log in. If the account is locked due to too many failed attempts, you will be notified.
*   **Register:** Create a new user account by providing a username, password, email, and phone number.

### 2. Lock Insights

*   Enter a username to analyze why their account might be locked.
*   Choose between "Classical Agent" and "GenAI Agent" to see different explanations for the account lock.

### 3. Recovery Assistant

*   Enter a username to initiate the account recovery process.
*   Select either "Classical Agent" or "GenAI Agent" to guide you through the recovery steps.
*   Follow the prompts to provide recovery information (e.g., registered email/phone, last transaction amount) and reset your password.

## Contributing

Feel free to fork the repository, open issues, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
