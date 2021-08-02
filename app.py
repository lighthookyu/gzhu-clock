from flask import Flask, jsonify, request

import spider as sp


def res_json(status=405, data="", msg="Bad request"):
    """
    格式化返回数据
    :param status: 状态码
    :param data: 主要数据
    :param msg: 响应信息
    :return: 完整响应请求的数据
    """
    res = {
        "data": data,
        "msg": msg,
        "status": status,
    }
    return jsonify(res)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

once = {}


@app.route("/clock-in", methods=["GET"])
def clock_in():
    username = request.args.get('username')
    password = request.args.get('password')

    try:
        spider = sp.GZHU(username, password)

        if once.get(spider.duplicate_key):
            data = spider.duplicate_key + " 已经打卡，请勿重复打卡"
            return res_json(status=400, msg=data)

        if spider.login():

            data = spider.clock_in(username)
            if data == "成功":
                once[spider.duplicate_key] = True
                return res_json(status=200, data=data, msg="request succeed")
            return res_json(status=500, msg=data)
        else:
            return res_json(status=401, msg='Unauthorized')

    except Exception as e:
        print("err:", e)
        return res_json(status=500, msg=str(e))


if __name__ == '__main__':
    app.run("0.0.0.0", threaded=True)
