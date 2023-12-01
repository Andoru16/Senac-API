from website import create_app
from os import environ

app = create_app()

if __name__ == '__main__':
   HOST = environ.get('SERVER_HOST', '0.0.0.0')
   try:
      PORT = int(environ.get('SERVER_PORT', '5555'))
   except ValueError:
      PORT = 5000
   app.run(HOST, PORT, debug=True)