# How to start project
*(If you're in pycharm all if this is done pretty much automatically, just set a new run configuration of fastapi and copy the .env.example to .env)*

1. **Create a virtual environment:**
   Python3 comes with a built-in module for creating virtual environments. You can create a virtual environment using the following command:

   ```bash
   python3 -m venv venv

2. **Activate the virtual environment:**

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    - Copy the example environment file to `.env`:

        ```bash
        cp .env.example .env
        ```

    - Open `.env` and populate the variables with your configuration:

        ```env
        API_KEY=your_openai_api_key_here
        ```

### Running the Application

1. **Start the FastAPI application using Uvicorn:**

    ```bash
    uvicorn app.main:app --reload
    ```

2. **Access the API documentation:**

   Open your web browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation.

# Deploy
```bash
docker build -t clerkai .
```

```bash
docker run --name clerkai -d -p 80:8000 -e  OPENAI_API_KEY=your_openai_api_key_here clerkai
```
