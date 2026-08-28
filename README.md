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





