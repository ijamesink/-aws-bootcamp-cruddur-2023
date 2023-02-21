FROM python:3.10-slim-buster

# Inside the container
# make a new folder
WORKDIR /backend-flask

# Outside Container -> Inside container
# This contains the libraries to be installed to run the app
COPY requirements.txt requirements.txt

# Inside the container
# It will install the python libraries for the app
RUN pip3 install -r requirements.txt

# Outside Container -> Inside Container
# first period . /backend-flask(Outside container)
# second period . /backend-flashk(Inside container)
COPY . .

# set inside container
ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]