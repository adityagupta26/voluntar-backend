from flask.views import MethodView
from flask import jsonify, request, g
from models import Operator
from config import PassHash, MIN_PASSWORD_LEN


def registerOperator(requestjson, created_by):
        """create a new user"""
        new_operator = requestjson
        # TODO: get authenticated operator and assignee to new Operator
        # new_operator["created_by"] = authenticated_oprator
        try:
            assert len(new_operator["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_operator["password"] = PassHash.hash(new_operator["password"])
            new_operator['created_by'] = created_by
            assert not Operator.objects(email=new_operator['email']) , "user with this email already exists"
            comment = Operator(**new_operator)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def updateOperator(requestjson, operator_id, delete=False):
        """update a single user by id"""
        print(operator_id, '---')
        update = {}
        if not delete:
            for key, value in requestjson.items():
                if key == '_id':
                    continue
                if key == "password":
                    value = PassHash.hash(value)
                update[f"set__{key}"] = value
        else:
            update["set__is_active"] = False

        try:
            Operator.objects(id=operator_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def getOperators(operator_id):
        try:
            if operator_id:
                operator = Operator.objects(id=operator_id).get().clean_data()
                return jsonify(operator)
            else:
                operator = [v.clean_data() for v in Operator.objects(is_active=True).all()]
                return jsonify({"list": operator})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


def getToken(username):
    operator = Operator.objects(email=username,is_active=True)#.get()#.clean_data()
    if operator:
        return operator.get().generate_auth_token()
    #print(operator)
    #g.user = operator
    return None

def verifyUser(username, password):
    user = Operator.verify_auth_token(username)#username_or_token
    if not user:
        operator = Operator.objects(email=username,is_active=True)#.get()#.clean_data()
        if operator:
            return operator.get().check_password(password)
        #print(operator)
        return False
    #g.user = operator
    return True


class OperatorAPI(MethodView):

    def get(self, operator_id:str):
        try:
            if operator_id:
                operator = Operator.objects(id=operator_id).get().clean_data()
                return jsonify(operator)
            else:
                operators = [v.clean_data() for v in Operator.objects(is_active=True).all()]
                return jsonify({"list": operators})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def post(self):
        """create a new user"""
        new_Operator = request.json
        # TODO: get authenticated operator and assignee to new Operator
        # new_Operator["created_by"] = authenticated_oprator
        try:
            assert len(new_Operator["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_Operator["password"] = PassHash.hash(new_Operator["password"])
            comment = Operator(**new_Operator)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


    def delete(self, operator_id):
        """delete a single user by id"""
        return self.put(operator_id, delete=True)

    def put(self, operator_id, delete=False):
        """update a single user by id"""
        update = {}
        if not delete:
            for key, value in request.json:
                if key == "password":
                    value = PassHash.hash(value)
                update[f"set__{key}"] = value
        else:
            update["set__is_active"] = False

        try:
            Operator.objects(id=operator_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400
