workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8080"
daemon = True
pidfile = "./main.pid"
pythonpath = "./"