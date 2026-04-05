from api.routes import app
import uvicorn
from api.routes import app
from data.models import init_db
import uvicorn

if __name__ == "__main__":
    init_db()
    uvicorn.run("api.routes:app", host="0.0.0.0", port=8000)

