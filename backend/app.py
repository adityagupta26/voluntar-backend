from flask import Flask
from endpoints import VolunteerAPI, Beneficiary_requestAPI,BeneficiaryAPI,OperatorAPI, telegrambot
from mongoengine import connect
from config import app, SWAGGERUI_BLUEPRINT, SWAGGER_URL, DB_NAME, DB_HOST

from endpoints import registerVolunteer, getVolunteers,updateVolunteer, verifyUser, getToken, \
		registerOperator, getOperators, updateOperator, \
		registerBeneficiary, getBeneficiary, updateBeneficiary, get_volunteers_by_filters, get_active_operator, get_beneficieries_by_filters, \
		get_operators_by_filters, sort_closest, registerTag, getTags, updateTag, parseFile, updateVolunteerTG, updateBeneficiaryTG

from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import os, json, random
auth = HTTPBasicAuth()

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

cors = CORS(app)

volunteer_view = VolunteerAPI.as_view('volunteers')
#app.add_url_rule('/volunteers/list/', defaults={'volunteer_id': None}, view_func=volunteer_view, methods=['GET',])
#app.add_url_rule('/volunteers/', view_func=volunteer_view, methods=['POST',])
#app.add_url_rule('/volunteers/<volunteer_id>', view_func=volunteer_view, methods=['GET', 'PUT', 'DELETE'])

connect(db=DB_NAME, host=DB_HOST)

#old school
@auth.verify_password
def verify_password(username, password):
	return verifyUser(username, password)
#volunteers
@app.route('/api/volunteer', methods = ['POST'])
@auth.login_required
def new_user():
	return registerVolunteer(request.json, auth.username())

@app.route('/api/volunteer', methods = ['GET'])
@auth.login_required
def get_user(): 
	return getVolunteers(request.args)#request.args.get('id'))


@app.route('/api/volunteer/filters', methods=['GET'])
@app.route('/api/volunteer/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_user_by_filters(pages=15, per_page=10):
	return get_volunteers_by_filters(request.args, pages, per_page)


@app.route('/api/volunteer', methods = ['PUT'])
@auth.login_required
def update_user():
	if '_id' not in request.json:
		return updateVolunteerTG(request.json, request.json.get('telegram_chat_id'), request.json.get('phone'))
	else:
		return updateVolunteer(request.json, request.json['_id'])


@app.route('/api/volunteer/closest', methods=['GET', 'POST'])
@app.route('/api/volunteer/closest/<id>/<topk>', methods=['GET', "POST"])
@auth.login_required
def get_closest_user(id, topk):
	return sort_closest(id, topk, request.args.get('category'))

@app.route('/api/volunteer', methods = ['DELETE'])
@auth.login_required
def delete_user():
	return updateVolunteer(request.json, request.json['_id'], True)


@app.route('/api/volunteer/parse/', methods = ['GET'])
@auth.login_required
def parse_user():
	url = request.args.get('url')
	b = request.args.get('b')
	e = request.args.get('e')
	return parseFile(url, b, e, request.args)

#tags

@app.route('/api/tag', methods = ['POST'])
@auth.login_required
def new_tag():
	return registerTag(request.json, auth.username())

@app.route('/api/tag', methods = ['GET'])
@app.route('/api/tag/<select>', methods=['GET'])
@auth.login_required
def get_tag(select='all'):
	return getTags(request.args.get('id'), select)

@app.route('/api/tag', methods = ['PUT'])
@auth.login_required
def update_tag():
	return updateTag(request.json, request.json['_id'])

@app.route('/api/tagedit', methods = ['GET',"POST"])
@auth.login_required
def update_tag_get():
	if request.method == 'POST':
		js = json.loads(request.form.get('json'))
		for it in js:
			it['is_active'] = 'true' if it['is_active'] else 'false'
			updateTag({k:v for k,v in it.items() if k is  not '_id'}, it['_id'])
		return jsonify(js)
	tg = getTags(False, request.args.get('name'), False)
	dd = []
	return '<form action="" method="post" ><textarea style="    width: 800px;  height: 400px;" name="json">'+json.dumps(tg, indent=4, sort_keys=True)+'</textarea><button>go</button></form>'
	return updateTag(request.args, request.args.get('_id'))

@app.route('/api/tag', methods = ['DELETE'])
@auth.login_required
def delete_tag():
	return updateTag(request.json, request.json['_id'], True)

#operators
@app.route('/api/operator', methods = ['POST'])
@auth.login_required
def new_operator():
	return registerOperator(request.json, auth.username())

@app.route('/api/operator', methods = ['GET'])
@auth.login_required
def get_operator():
	return getOperators(request.args.get('id'))

@app.route('/api/operator', methods = ['PUT'])
@auth.login_required
def update_operator():
	return updateOperator(request.json, request.json['_id'])

@app.route('/api/operator', methods = ['DELETE'])
@auth.login_required
def delete_operator():
	return updateOperator(request.json, request.json['_id'], True)

@app.route('/api/operator/filters', methods=['GET'])
@app.route('/api/operator/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_operator_by_filters(pages=15, per_page=10):
	return get_operators_by_filters(request.args, pages, per_page)

#authentification
@app.route('/api/token', methods = ['GET', 'POST'])
@auth.login_required
def get_auth_token():
    token, data = getToken(auth.username())#g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


#beneficiari
@app.route('/api/beneficiary', methods = ['POST'])
@auth.login_required
def new_beneficiary():
    fixer_id = get_active_operator()
    return registerBeneficiary(request.json, auth.username(), fixer_id)

@app.route('/api/beneficiary', methods = ['GET'])
@auth.login_required
def get_beneficiary():
	return getBeneficiary(request.args)


@app.route('/api/secret', methods = ['GET'])
@auth.login_required
def get_secret():
	return jsonify({'secret' : random.choice('abcdefghijklmnopqrstuvwxyz').upper()+ str(random.choice(range(1000)))})


@app.route('/api/beneficiary', methods = ['PUT'])
@auth.login_required
def update_beneficiary():
	if 'wellbeing' in request.json:
		return updateBeneficiaryTG(request.json)
	return updateBeneficiary(request.json, request.json['_id'])


@app.route('/api/beneficiary/filters', methods=['GET'])
@app.route('/api/beneficiary/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_beneficiary_by_filters(pages=15, per_page=10):
	return get_beneficieries_by_filters(request.args, pages, per_page)

#debug part
@app.route('/api/debug', methods = ['GET'])
def get_user3():
	return jsonify(verifyUser('example@mail.com', 'Adm23232in1234'))

@app.route('/')
def hello():
	#str(get_active_operator())
	return  registerOperator({'email':os.environ["DEFAULT_USERNAME"],'password':os.environ["DEFAULT_PASSWORD"],'role':['fixer'], 'phone':10000001}, 'admin')
	return ("Hello world"+str(get_active_operator())+ '--'+str(request.args)+'-'+str(r))


@app.route('/api/receipt', methods=['POST'])
def upload_image():
	return telegrambot.save_receive(request.json['beneficiary_id'], request.json['data'])


if __name__ == "__main__":
	#registerOperator({'email':'test@test.com','password':'adminadmin','role':'fixer', 'phone':10000001})#todo: get from enviroment pass
	app.run(host="0.0.0.0", debug=True)