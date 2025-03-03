from app import app

# Esse arquivo serve como um ponto de entrada claro para o Uvicorn
# Ele importa a aplicação FastAPI da pasta app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 