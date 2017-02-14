#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import sys, json
import logging,inspect
import pymysql
import io,uuid
import hashlib




name = 'Val'

logging.basicConfig(format='[%(lineno)i: %(levelname)s:%(asctime)s]-> %(message)s', filename='/tmp/saveList.log',
                    datefmt='%m-%d-%Y %I:%M:%S(%p)',
                    func=None,
                    level=logging.DEBUG,
                    )
#logging.LogRecord(name,func=None, sinfo=None)

def connToMysql():
    return pymysql.connect("localhost", "root", "352352", "demoUser")



# save data in database
#
#

def createTableIfNeeded(cursor,json_FromCliDecoded):
    hashId = json_FromCliDecoded['aTask'][0]['hashId']
    logging.info("createTableIfNeeded hashId for table cration is :" + hashId)
    lenDesc = len(json_FromCliDecoded['aTask'][0]['taskText'])
    logging.info("before try catch in write mode")
    try:
        cursor.execute('SELECT 1 FROM `%s` LIMIT 1' % (hashId))
        logging.debug("Talble does exist")
    except:
        # print("programming error")
        logging.info("gonna create table with '%s'" % (hashId))
        sql = """CREATE TABLE `%s`(
                       ID  TEXT (%d)NOT NULL,
                       taskText  TEXT(%d),
                       taskTime FLOAT(50),
                       lTime TEXT,
                       isDone BOOL,
                       hashId TEXT)""" % (hashId, lenDesc, 100)
        logging.debug(sql)
        cursor.execute(sql)
        db.commit()
        logging.debug("table created")


def writeToMysql(cursor,json_FromCliDecoded):

        # logging.info("a Task is :  + aTask)
        # choose hashId of mainTable

        mainHashId = chooseAHash(json_FromCliDecoded)
        #print(cursor.fetchone())
        logging.debug("inserting to a table '%s' " %(mainHashId))

        json_FromCliDecoded['aTask'][0]['state'] = "update"
        if  (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
              json_FromCliDecoded['aTask'][0]['hashId'] = mainHashId
              createTableIfNeeded(cursor, json_FromCliDecoded)


        # table created add entry to this table
        # choose hashId for task in
        json_FromCliDecoded['aTask'][0]['hashId'] = chooseAHash(json_FromCliDecoded)

        if (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
            createTableIfNeeded(cursor, json_FromCliDecoded)
        # table created add entry to this table
        sqlIns = """INSERT INTO `%s` (
                      ID,taskText,taskTime,lTime,isDone,hashId)
                      VALUES ('%s', '%s', '%0.2f','%s', %s, '%s')""" % (mainHashId,json_FromCliDecoded['aTask'][0]['id'],
                                                  json_FromCliDecoded['aTask'][0]['taskText'],
                                                  float(json_FromCliDecoded['aTask'][0]['taskTime']),
                                                  json_FromCliDecoded['aTask'][0]['lTime'],
                                                  False,
                                                  json_FromCliDecoded['aTask'][0]['hashId'])

        logging.info("var was prepared: '%s'" % (sqlIns))
        try:
            cursor.execute(sqlIns)
        except Exception as e:
            logging.error(e)
            return 'ERROR:in writeToMysql(). Insert failed!'
        logging.info("inserting done")
        db.commit()
        # it is not the best solution to get it from mysql after inserting,but not so bad too
        logging.info("going to get created row from mySql")
        # hashOfATask
        logging.debug("current hash id in writeToMysql is: '%s'" % (json_FromCliDecoded['aTask'][0]['hashId']))
        json_FromCliDecoded['aTask'][0]['state'] = "write"
        json_FromCliDecoded['aTask'][0]['mainHash'] = mainHashId
        return getFromMySql(cursor,json_FromCliDecoded)



#choosing hashId depending on state and  current page
def chooseAHash(json_FromCliDecoded):
    logging.debug("in choose hash 1")
    pageIs = json_FromCliDecoded['aTask'][0]['pageIs']
    logging.debug("in choose hash 2")
    state = json_FromCliDecoded['aTask'][0]['state']
    logging.info("Page is: '%s' current state: '%s' " % (pageIs,state))
    mainHashId=""
    # if (pageIs == "mainPage"):
    NotHashedTable = json_FromCliDecoded['aTask'][0]['aUser'] + "title"
    mainHashId = hashlib.sha256(NotHashedTable.encode('utf-8')).hexdigest()
    logging.debug("main hash id is '%s'" % mainHashId)

    if (pageIs == "mainPage" and state == "write"):
        return mainHashId

    if (pageIs == "mainPage" and state == "update"):
        salt = uuid.uuid4().hex
        NotHashedTable = json_FromCliDecoded['aTask'][0]['aUser'] + json_FromCliDecoded['aTask'][0]['id'] + json_FromCliDecoded['aTask'][0]['taskText'] + salt
        hashId = hashlib.sha256(NotHashedTable.encode('utf-8')).hexdigest()
        return hashId

    if ((pageIs == "aSubTask" and state == "write") or (pageIs == "aSubTask" and state == "pageHasLoaded")):
        return json_FromCliDecoded['aTask'][0]['hashId']

    if(pageIs == "aSubTask" and state == "update"):
        salt = uuid.uuid4().hex
        NotHashedTable = json_FromCliDecoded['aTask'][0]['aUser'] + json_FromCliDecoded['aTask'][0]['id'] + json_FromCliDecoded['aTask'][0]['taskText'] + salt
        hashId = hashlib.sha256(NotHashedTable.encode('utf-8')).hexdigest()
        logging.debug("aSubTask in chooseHash: '%s'" %(hashId))
        return hashId

    if (pageIs == "aSubTask" and state == "remove" or
            (pageIs == "aSubTask" and state == "done") or
             pageIs == "aSubTask" and state == "edit"):
       logging.debug("hash gonna be returned for aSubTask")
       return json_FromCliDecoded['aTask'][0]['subTaskHash']
    logging.debug("main hash id gonna be returned")
    return mainHashId






def makeAJsonForCl(rows,cursor,state):


    list_ = []
    namesOfColumns = []
    for i in range (len(cursor.description)):
        namesOfColumns.append(cursor.description[i][0])
    i = 0
    # list_.append('"aTask":')
    # list_.append("[")
    for row in rows:
        list_.append("{")
        for cell in row:
            list_.append('"' + namesOfColumns[i] + '"' + ':' + '"' + str(cell) + '"')
            i += 1
            if i != (len(namesOfColumns)):
                list_.append(",")
        list_.append("}")
        list_.append(",")
        i = 0
    # remove last comma
    # list_.pop()
    # list_.append("]")
    joinedList = ''.join(list_)
    additional_state = '{"answer":'+ '"' + state + '"' + '}'
    json_string = '{"aTask": [' + joinedList + additional_state + ']}'
    #json_string = '{"aTask": ['  + joinedList + ']}'
    #logging.debug("with additional state '%s'" % (json_string_test))
    logging.debug("makeAJsonForCl: '%s'" % (json_string))
    return json_string






#Get data from data base
#
#

def getFromMySql(cursor,json_FromCliDecoded):

    mainHashId=""
    hashId=""
    sql=""

    logging.debug("getFromMySql: pageIs: '%s', state is:'%s'" % (json_FromCliDecoded['aTask'][0]['pageIs'],json_FromCliDecoded['aTask'][0]['state']))
    if(json_FromCliDecoded['aTask'][0]['state'] == "write"):

        logging.debug("getFromMySql was called from Write function mainHashId '%s' aTaskHashId '%s'",
                      mainHashId, json_FromCliDecoded['aTask'][0]['hashId'])

        mainHashId = json_FromCliDecoded['aTask'][0]['mainHash']
        sql = "SELECT * FROM `%s` WHERE hashId='%s' " % (mainHashId,json_FromCliDecoded['aTask'][0]['hashId'])
        logging.debug(sql)
        try:
            cursor.execute(sql)
        except pymysql.MySQLError as e:
            logging.error("the error: %d , has: %s ", e.args[0], e.args[1])
        rows = cursor.fetchall()
        return makeAJsonForCl(rows, cursor,'written')
    else:
        logging.info("get from Mysql")
        hashId = chooseAHash(json_FromCliDecoded)
        sql = "SELECT COUNT(*) FROM `%s` " % (hashId)


    try:
        cursor.execute(sql)
    except pymysql.MySQLError as e:
        logging.error("the error: %d , has: %s ",e.args[0],e.args[1])
        return 'noTable'


    logging.info("executed successfully")
    countX = cursor.fetchall()

    logging.debug("Feteched data is: '%s', first element of fetched data is : '%s' " % (countX,countX[0][0]))
    if countX[0][0] == 0:
        logging.debug("Going to return noField")
        return 'noField'
    #print("testingcall")
    logging.debug("assign sql variable")
    sql = "SELECT * FROM `%s`" % (hashId)
    logging.debug("sql variable has been assigned '%s'" %(sql))

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except  pymysql.MySQLError as e:
        logging.error("fail to fetched data: %d , has: %s ", e.args[0], e.args[1])

    return makeAJsonForCl(rows,cursor,'get')



#if user updates column
#
#
def updateTable(cursor, json_FromCliDecoded):
    logging.info("in update func")
    taskTimeTemp = json_FromCliDecoded['aTask'][0]['taskTime']
    logging.info(taskTimeTemp)
    taskTextTemp = json_FromCliDecoded['aTask'][0]['taskText']
    taskTimeTemp = float(taskTimeTemp)
    logging.info("updateTable taskTexTemp '%s'"  % taskTextTemp)
    hashId = chooseAHash(json_FromCliDecoded)

    logging.debug("what is hash for task to be changed '%s'" % (json_FromCliDecoded['aTask'][0]['hashId']))
    if (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
        logging.debug("update,mainPage")
        sql = "UPDATE %s SET taskText='%s',taskTime=%s where hashId='%s'" % (hashId, json_FromCliDecoded['aTask'][0]['taskText'], taskTimeTemp, json_FromCliDecoded['aTask'][0]['hashId'])
        cursor.execute(sql)
    else:
        sql = "UPDATE %s SET taskText='%s',taskTime=%s where hashId='%s'" % (json_FromCliDecoded['aTask'][0]['hashId'], json_FromCliDecoded['aTask'][0]['taskText'],taskTimeTemp, hashId)
        logging.debug(sql)

    cursor.execute(sql)
    db.commit()
    json_FromCliDecoded['aTask'][0]['answer'] = "edited"
    return str(json_FromCliDecoded)

def deleteTask(cursor, json_FromCliDecoded):

    logging.debug("what is hash for deleted task '%s'" %(json_FromCliDecoded['aTask'][0]['hashId']))
    hashId = chooseAHash(json_FromCliDecoded)
    if (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
         sql = "DELETE FROM `%s` WHERE hashId='%s'" % (hashId, json_FromCliDecoded['aTask'][0]['hashId'])
         logging.debug("delete command for main page: '%s'" % (sql))
    else:
         sql = "DELETE FROM `%s` WHERE hashId='%s'" % (json_FromCliDecoded['aTask'][0]['hashId'],hashId)
         logging.debug("delete command for subTask page: '%s'" % (sql))

    logging.info("In delete Task")
    logging.debug("delete command: '%s'" % sql)
    cursor.execute(sql)
    db.commit()
    if (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
        sql = "DROP TABLE `%s`" % (json_FromCliDecoded['aTask'][0]['hashId'])
    logging.debug("delete command: '%s'" % sql)
    cursor.execute(sql)
    logging.info("deleted")
    json_FromCliDecoded["answer"] = "removed"

    return str(json_FromCliDecoded)

def doneTask(cursor, json_FromCliDecoded):
    logging.debug("in done task")
    if json_FromCliDecoded['aTask'][0]['isDone'] == "true":
        isDone = True
        logging.info("isDone is")
        logging.info(isDone)
    else:
        isDone = False
        logging.info(isDone)

    hashId = chooseAHash(json_FromCliDecoded)
    if (json_FromCliDecoded['aTask'][0]['pageIs'] == "mainPage"):
         sql = "UPDATE `%s` SET isDone=%s WHERE hashId='%s'" % (hashId,isDone,json_FromCliDecoded['aTask'][0]['hashId'])
         logging.debug("done command for main page: '%s'" % (sql))
    else:
         sql = "UPDATE `%s` SET isDone=%s WHERE hashId='%s'" % (json_FromCliDecoded['aTask'][0]['hashId'],isDone,hashId)
         logging.debug("done command for subTask page: '%s'" % (sql))
    cursor.execute(sql)
    json_FromCliDecoded["answer"] = "itsDone"
    return str(json_FromCliDecoded)




if __name__ == '__main__':

    forClient = ""
    db = connToMysql()
    db.set_charset('utf8')
    cursor = db.cursor()
    cursor.execute("USE demoUser")
   # data4 = '{"aTask":  [{"id": "1", "taskText": "trying update second","taskTime": "2.5", "lTime": "2016-10-01; 22:22:22", "isDone": "false", "isEdited":"true"}]}'
    #for debug purposes
    data4 = '{"aTask": [{' + '"state":"pageIsLoaded"' + '}]}'
    json_FromCliDecoded = " "
    logging.info("before")
    try:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        data4 = json.load(input_stream)
        json_FromCliDecoded = json.loads(data4)
    except Exception as e:
        logging.error(e)
        logging.error(data4)

    # if data4 == "pageIsLoaded":
    #     forClient = getFromMySql(cursor)
    #print("passed try catch trapped")

    logging.info(json_FromCliDecoded)
    if json_FromCliDecoded['aTask'][0]['state'] == "write":
        logging.info("gonna write to mysql")
        forClient = writeToMysql(cursor, json_FromCliDecoded)
    elif json_FromCliDecoded['aTask'][0]['state'] == "edit":
        logging.info("update if")
        forClient = updateTable(cursor, json_FromCliDecoded)
    elif json_FromCliDecoded['aTask'][0]['state'] == "done":
        logging.info(forClient)
        forClient = doneTask(cursor, json_FromCliDecoded)
    elif json_FromCliDecoded['aTask'][0]['state'] == "remove":
        #logging.info("removing" + json_FromCliDecoded['aTask'][0])
        forClient = deleteTask(cursor, json_FromCliDecoded)
    elif json_FromCliDecoded['aTask'][0]['state'] == "pageHasLoaded":
        logging.debug("going to get getFromMySql aTask '%s'" % (json_FromCliDecoded['aTask'][0]['state']))
        forClient = getFromMySql(cursor,json_FromCliDecoded)
    elif json_FromCliDecoded['aTask'][0]['state'] == "register":
        logging.debug("register")
        logging.debug("register '%s'" % (json_FromCliDecoded['aTask'][0]['aUser']))
        # createAUser(cursor,json_FromCliDecoded)
        # doesn't work and I have no idea why
        # print "HTTP/1.1 303 See Other"
        # print("Location: http://example.org/other?user=xyz")


    db.commit()

    logging.debug("message for client: '%s'" % (forClient))
    db.close()
    print("Content-Type: application/json\n\n")
    #logging.debug(forClient)
    print(json.dumps(forClient))



