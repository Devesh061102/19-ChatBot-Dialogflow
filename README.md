# 19-ChatBot-Dialogflow

**Project Structure**

* **backend** (Python): Contains the FastAPI backend code that powers the application.
* **db** (Database): Stores the database structure (schema) and optional sample data. You'll need to import this into your MySQL database using MySQL Workbench.
* **dialogflow_assets** (Dialogflow): Holds training phrases and other resources used to define intents within Google Dialogflow for chatbot interactions (if applicable).
* **frontend** (Website Code): Includes the code for the user interface and client-side logic of your web application.

**Installation**

1. **Prerequisites:** Ensure you have Python 3 and `pip` (Python package manager) installed.
2. **Install Dependencies:**
   - **Option 1: Individual Packages:**
     ```bash
     pip install mysql-connector
     pip install "fastapi[all]"
     ```
   - **Option 2: Requirements File (Recommended):**
     The `backend/requirements.txt` file specifies all necessary dependencies. Simply run:
     ```bash
     pip install -r backend/requirements.txt
     ```

**Running the Application**

1. **Navigate to Backend Directory:** Open a command prompt or terminal and change directories to the `backend` folder.
2. **Start FastAPI Server:** Execute the following command to launch the development server:
   ```bash
   uvicorn main:app --reload
   ```
   - This command uses `uvicorn`, a web server library, to run the FastAPI application defined in the `main.py` file with the `app` variable as the entry point.
   - The `--reload` flag automatically restarts the server whenever you make changes to your code, streamlining the development process.

**Optional: ngrok for HTTPS Tunneling**

**Note:** This step might be necessary if you want to make your locally running application accessible from a public URL outside of your network for testing or demonstration purposes.

1. **Download ngrok:** Visit [https://ngrok.com/download](https://ngrok.com/download) and download the ngrok version compatible with your operating system.
2. **Extract and Run ngrok:** Extract the downloaded ZIP file and place the `ngrok.exe` (or `ngrok` on macOS/Linux) in a convenient location. Open a command prompt and navigate to that directory. Execute the following command, replacing `8000` with the port your FastAPI server is running on (usually 8000):
   ```bash
   ngrok http 8000
   ```
   - ngrok will create a temporary public URL that you can use to access your application in a web browser. This URL typically takes the format `https://<subdomain>.ngrok.io`.
