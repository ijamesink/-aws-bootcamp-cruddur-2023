from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os
# from flask_awscognito import AWSCognitoAuthentication

from service.users_short import *
from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *
from lib.cognito_jwt_token import CognitoJwtToken, extract_access_token, TokenVerifyError

# HoneyComb ................
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# X-RAY ............
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# HoneyComb....
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

# X-RAY................
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)

# show this in the logs within the backend-flask app (STDOUT)
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

cognito_jwt_token = CognitoJwtToken(
  user_pool_id = os.getenv('AWS_COGNITO_USER_POOL_ID'),
  user_pool_client_id = os.getenv('AWS_COGNITO_USER_POOL_CLIENT_ID'),
  region = os.getenv('AWS_DEFAULT_REGION')
)

# app.config['AWS_COGNITO_USER_POOL_ID'] = os.getenv('AWS_COGNITO_USER_POOL_ID')
# app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = os.getenv('AWS_COGNITO_USER_POOL_CLIENT_ID') -- throwing errors therefore removed from the code

# aws_auth = AWSCognitoAuthentication(app)

# X-RAY..........
XRayMiddleware(app, xray_recorder)

# HoneyComb....
# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

frontend = os.getenv('FRONTEND_URL')
backend = os.getenv('BACKEND_URL')
origins = [frontend, backend]
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)

@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    app.logger.debug('authenticated')
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    model = MessageGroups.run(cognito_user_id = cognito_user_id)
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unathenticated request
    app.logger.debug(e)
  return {}, 401
  
 
 @app.route('/api/health-check')
def health_check():
  return {'success': True}, 200


@app.route("/api/messages/<string:message_group_uuid>", methods=['GET'])
def data_messages(message_group_uuid):
  # user_sender_handle = 'andrewbrown'
  # user_receiver_handle = request.args.get('user_receiver_handle')

  # model = Messages.run(user_sender_handle=user_sender_handle, user_receiver_handle=user_receiver_handle)
  model = Messages.run(message_group_uuid=message_group_uuid)

  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    app.logger.debug('authenticated')
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    model = Messages.run(
      cognito_user_id = cognito_user_id,
      message_group_uuid=message_group_uuid
    )
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unathenticated request
    app.logger.debug(e)
  return {}, 401

@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
def data_create_message():
  message_group_uuid = request.json.get('message_group_uuid', None)
  user_receiver_handle = request.json.get('handle', None)
  message = request.json['message']

  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    app.logger.debug('authenticated')
    app.logger.debug(claims)
    cognito_user_id = claims['sub']
    if message_group_uuid == None:
    # Create for the first time
    model = CreateMessage.run(
      mode="create",
      message=message,
      cognito_user_id=cognito_user_id,
      user_receiver_handle=user_receiver_handle
    )
    else:
    # Push onto existing Message Group
    model = CreateMessage.run(
      mode="update",
      message=message,
      message_group_uuid=message_group_uuid,
      cognito_user_id=cognito_user_id
    )
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unathenticated request
    app.logger.debug(e)
  return {}, 401


@app.route("/api/activities/home", methods=['GET'])
@xray_recorder.capture('activities_home')
# @aws_auth.authentication_required
def data_home():
  # app.logger.debug('AUTH HEADER')
  # app.logger.debug(
  #   request.headers.get('Authorization')
  # )
  access_token = extract_access_token(request.headers)
    try:
      claims = cognito_jwt_token.verify(access_token)
      # self.claims = self.token_service.claims
      # g.cognito_claims = self.claims
      # authenticated request
      app.logger.debug('authenticated')
      app.logger.debug(claims)
      app.logger.debug(claims['username'])
      data = HomeActivities.run(cognito_user_id = claims['username'])
    except TokenVerifyError as e:
      _ = request.data
      # unathenticated request
      app.logger.debug(e)
      app.logger.debug('unauthenticated')
      # abort(make_response(jsonify(message=str(e)), 401))
      # claims = aws_auth.claims
    
    data = HomeActivities.run()
    return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200

@app.route("/api/activities/@<string:handle>", methods=['GET'])
@xray_recorder.capture('activites_users')
def data_handle(handle):
  model = UserActivities.run(handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

@app.route("/api/activities/search", methods=['GET'])
def data_search():
  term = request.args.get('term')
  model = SearchActivities.run(term)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities():
  user_handle  = 'andrewbrown'
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, user_handle, ttl)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route('/api/users/@<string:handle>/short', methods=['GET'])
def data_users_short(handle):
  data = UserShort.run(handle)
  return data, 200

if __name__ == "__main__":
  app.run(debug=True)