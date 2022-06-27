import os, pathlib; os.chdir(pathlib.Path(__file__).parent)
from app import app
import routes

app.run(debug=True)

