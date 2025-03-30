import uvicorn

from web.app_wss.main import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True, auto_reload=False)
    # uvicorn.run(app=app, host='0.0.0.0', port=8001)