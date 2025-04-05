import uvicorn

from functools import partial

from sanic import Sanic
from sanic.worker.loader import AppLoader
from web.app_wss.main import create_app

# app = create_app()

if __name__ == '__main__':
    loader = AppLoader(factory=partial(create_app))
    app = loader.load()
    app.prepare(host='0.0.0.0', port=8001, debug=True, auto_reload=False)
    Sanic.serve(primary=app, app_loader=loader)

    # app.run(host='0.0.0.0', port=8001, debug=True, auto_reload=False)
    
    # uvicorn.run(app=app, host='0.0.0.0', port=8001)
    # uvicorn.run("web.app_wss.main:create_app", host='0.0.0.0', port=8001, workers=2, reload=False)