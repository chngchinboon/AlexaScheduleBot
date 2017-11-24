import logging
rootLogger = logging.getLogger(__name__)

def get_pledge_msg(msg_info):
    rootLogger.info('pledge message')
    pledge_msg=get_info_from_SB(msg_info)
    rootLogger.info('Get pledge complete')
    rootLogger.debug(pledge_msg)
    return pledge_msg

def get_info_from_SB(param):
    if param['db_name'] == 'devdb':
        # get from database #to be removed
        db = sqlite3.connect('../data/testdb')
        db.row_factory = dict_factory
        cursor = db.cursor()
        cursor.execute('select * from ' + db_name + ' where username = "user1"')
        data_retrieved = cursor.fetchall()
        db.close()

    # retrieve data from SB
    else:
        # build object to be sent. redundant?
        data_to_send={'Alexa_id': param['user_id']}
        rootLogger.debug(data_to_send)
        # Send request to SB
        # try:
        #    r = requests.post('http://httpbin.org/post', data = {'key':'value'})
        #    r = RQ.post(url, json = data_to_send)

        # parse return data from PICA
        # iso8601.parse_date()
        # time of the appointment
        # type of service (e.g. meal service)
        # assigned healthcare worker
        # comments (this is optional e.g. assigned careworker will be running late)
        # data_recieved = r.json()
        data_retrieved = data_to_send

    return data_retrieved

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d