import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Start the uvicorn server using import string to enable reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)