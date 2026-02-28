from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Protección de Activos",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "mensaje": "Sistema Integral de Protección de Activos API",
        "version": "1.0.0",
        "status": "✅ Operativo",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
```

4. **Commit**

---

### PASO 3: Cambiar Start Command en Render

1. **En Render → Settings**

2. **Start Command cambiar a:**
```
uvicorn app:app --host 0.0.0.0 --port $PORT
