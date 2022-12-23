# Import the create_app function from the website folder
from website import create_app

app = create_app()

# Check to see if script is being run directly or as a module. If directly, then run 
if __name__ == "__main__": 
    # Start the server and run app, debug true means changes in code are reflected in the app in real time. 
    app.run(debug=True)
