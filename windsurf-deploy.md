# 🚀 Windsurf Deployment Commands

## **Option 1: Deploy with Windsurf CLI**

```bash
windsurf deploy --project-name "ds-inventory-server" \
  --build-command "pip install -r requirements-minimal.txt && python add_name_column.py" \
  --start-command "gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker" \
  --env "PYTHONUNBUFFERED=1" \
  --env "SECRET_KEY=your-secret-key-change-this"
```

## **Option 2: Alternative with Uvicorn**

```bash
windsurf deploy --project-name "ds-inventory-server" \
  --build-command "pip install -r requirements-minimal.txt && python add_name_column.py" \
  --start-command "python start.py" \
  --env "PYTHONUNBUFFERED=1" \
  --env "SECRET_KEY=your-secret-key-change-this"
```

## **Option 3: Simple Flask-style**

```bash
windsurf deploy --project-name "ds-inventory-server" \
  --build-command "pip install -r requirements-minimal.txt" \
  --start-command "gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker" \
  --env "PYTHONUNBUFFERED=1"
```

## **Environment Variables to Set:**
- `SECRET_KEY`: Your secret key for JWT tokens
- `PYTHONUNBUFFERED`: Ensures Python output is sent straight to terminal
- `DATABASE_URL`: If using external database (optional for SQLite)

## **Prerequisites:**
1. Install Windsurf CLI
2. Navigate to backend directory
3. Ensure all files are committed to git
4. Run the deployment command

## **Expected Result:**
- ✅ Automatic build and deployment
- ✅ Proper port binding to Windsurf's dynamic port
- ✅ Production-ready gunicorn server
- ✅ Environment variables configured

## **Advantages of Windsurf:**
- Simpler than Render configuration
- Better error handling
- Automatic SSL certificates
- Built-in monitoring
- Direct CLI deployment
