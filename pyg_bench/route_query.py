import re

routingtable = {
    'route': [
        {
            'usernameRegex': '.*',
            'queryRegex': '.*SELECT.*',
            'dbkey': 'server.2'
        }
    ]
}


def routing_rules(username, query):
    for route in routingtable['route']:
        u = re.compile(route['usernameRegex'])
        q = re.compile(route['queryRegex'])
        if u.search(username) and q.search(query):
            print("returning: {}".format(route['dbkey']))
            return route['dbkey']
    return 'server.1'
