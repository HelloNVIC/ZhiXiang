
import webbrowser
import subprocess
import threading
import time
import os

HOST = "0.0.0.0"  
PORT = 8000

def start_backend():
    """使用 subprocess 启动 uvicorn 服务器。"""
    print(f"--- 后端启动中，请访问 http://{HOST}:{PORT} ---")
    subprocess.run(
        [os.sys.executable, "-m", "uvicorn", "app:app", f"--host={HOST}", f"--port={PORT}"]
    )

def open_frontend():
    """在默认浏览器中打开前端页面。"""

    time.sleep(1)
    url = f"http://{HOST}:{PORT}"
    
    print(f"--- 在默认浏览器中打开前端: {url} ---")
    webbrowser.open(url)

if __name__ == "__main__":

    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True 
    backend_thread.start()
    open_frontend()


    try:
        backend_thread.join()
    except KeyboardInterrupt:
        print("\n--- 程序已关闭 ---")
        os._exit(0)