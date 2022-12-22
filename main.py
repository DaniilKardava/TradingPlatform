from website import create_app

app = create_app()

if __name__ == "__main__": 
    # debug True reruns web app everytime we change code
    app.run(debug=True)
