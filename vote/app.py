from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json

exp_docker_low = os.getenv('EXP_OPTION_A', "exp_docker_low")
exp_docker_medium = os.getenv('EXP_OPTION_B', "exp_docker_medium")
exp_docker_high = os.getenv('EXP_OPTION_C', "exp_docker_high")

want_docker_low = os.getenv('WANT_OPTION_A', "want_docker_low")
want_docker_medium = os.getenv('WANT_OPTION_B', "want_docker_medium")
want_docker_high = os.getenv('WANT_OPTION_C', "want_docker_high")

hostname = socket.gethostname()

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    exp_vote = None
    want_vote = None

    if request.method == 'POST':
        redis = get_redis()
        exp_vote = request.form['exp_vote']
        want_vote = request.form['want_vote']
        data = json.dumps({'voter_id': voter_id, 'exp_vote': exp_vote, 'want_vote': want_vote})
        redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',

        exp_docker_low=exp_docker_low,
        exp_docker_medium=exp_docker_medium,
        exp_docker_high=exp_docker_high,

        want_docker_low=want_docker_low,
        want_docker_medium=want_docker_medium,
        want_docker_high=want_docker_high,

        hostname=hostname,

        exp_vote=exp_vote,
        want_vote=want_vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
