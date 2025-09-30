from flask import render_template,jsonify
import modules.dbmanage as dbm
from datetime import datetime
from ast import literal_eval
import re
import pandas as pd

def valid_mail(mail):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mail)

def user_list():
    obj = dbm.users()
    out = []
    for i in obj.get():
        out.append(list(i))
    return out



def check(key,data,strict=False):
    for x in data:
        for i in x:
            i = str(i).lower()
            if(not strict):
                if(key in i or key == i):
                    return x
            else:
                if(key == i):
                    return x
    return False


def search(query, admin=False):
    match query[0].lower():
        case "user":
            if not admin:
                return jsonify({"error": "Unauthorized action"}), 403
            
            obj = dbm.users()
            result = check(query[1], obj.get(),strict=True)
            if result:
                return jsonify({"type": "user", "result": result})
            else:
                return jsonify({"error": f"No { query[0] } found for \'{ query[1] }\'"}), 404

        case "subject":
            obj = dbm.subject()
            result = check(query[1], obj.get())
            if result:
                return jsonify({"type": "subject", "result": result})
            else:
                return jsonify({"error": f"No { query[0] } found for \'{ query[1] }\'"}), 404

        case "chapter":
            obj = dbm.chapter()
            result = check(query[1], obj.get())
            if result:
                result = list(result)
                result[1] = subswap(result[1])
                return jsonify({"type": "chapter", "result": result})
            else:
                return jsonify({"error": f"No { query[0] } found for \'{ query[1] }\'"}), 404

        case "quiz":
            obj = dbm.quiz()
            result = check(query[1], obj.get())
            if result:
                result = list(result)
                result.extend(chapswap(result[1]))
                return jsonify({"type": "quiz", "result": result})
            else:
                return jsonify({"error": f"No { query[0] } found for \'{ query[1] }\'"}), 404

        case "question":
            obj = dbm.questions()
            result = check(query[1], obj.get())
            if result:
                result = list(result)
                result = process_quest(result)
                result.extend(quizswap(result[1]))
                if(not admin):
                    result.pop(4)
                return jsonify({"type": "question", "result": result})
            else:
                return jsonify({"error": f"No { query[0] } found for \'{ query[1] }\'"}), 404

        case _:
            return jsonify({"error": "Invalid search type"}), 400
