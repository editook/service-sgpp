# 

# 

# service-sgpp

servicio de consumo de peritos
desde python -m app.create\_admin
para ejecutar scripts en tiempo de ejecucion(local):
.\\venv\\Scripts\\python.exe -m app.create\_admin

en local: .\\venv\\Scripts\\python -m uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload
en produccion: cd service-sgpp \&\& .\\venv\\Scripts\\activate \&\& python -m uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload



frontend-sgpp: npm.cmd run dev



start "Backend SGPP" cmd /k "cd service-sgpp \&\& .\\venv\\Scripts\\activate \&\& python -m uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload"




#configuracion segun entorno postgres|sqlite
DATABASE_URL: str = "postgresql://postgres:123@localhost:5432/gestion_pericial"
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sgpp_test.db")

url = self.DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///./sgpp_test.db")
url = self.DATABASE_URL or os.getenv("DATABASE_URL", "")