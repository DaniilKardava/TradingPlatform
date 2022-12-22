from website import create_app
from subprocess import Popen


def run_server():
    server = Popen(['node', 'serverSideData.js'])
    return server


app = create_app()

if __name__ == "__main__":
    server = run_server()
    # debug True reruns web app everytime we change code
    app.run(debug=True)
