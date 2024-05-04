workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:9090"
daemon = True
pidfile = "./main.pid"
pythonpath = "./"
