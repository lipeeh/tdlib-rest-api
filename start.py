#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    # Define a porta através da variável de ambiente ou usa 8000 como padrão
    port = int(os.environ.get("PORT", 8000))
    
    # Inicia o servidor uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    ) 