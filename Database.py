
import sqlite3
import wikipedia


class Database:

    def __init__(self):
        self.base = sqlite3.connect('./city.db')
        self.cur = self.base.cursor()

    def createTable(self):
        self.base.execute('CREATE TABLE IF NOT EXISTS {}(firstletter, name, picid text)'.format('city'))
        self.base.execute('CREATE TABLE IF NOT EXISTS {}(id, tgid, path, move)'.format('game'))
        self.base.commit()
        print("Created db")

    def addindb(self, name: str):
        fletter = name[0].lower()
        language = "ru"
        wikipedia.set_lang(language)
        wikipage = wikipedia.page(name)
        image = wikipage.images[0]
        for i in range(len(wikipage.images)):
            img = wikipage.images[i]
            if img[-4:] != '.svg':
                image = wikipage.images[i]
                break
        self.cur.execute('INSERT INTO city(name, firstletter, picid) VALUES (?, ?, ?)', (name, fletter, image))
        self.base.commit()

    def getcity(self, fletter):
        city = self.cur.execute('SELECT name FROM city WHERE firstletter == ?', (fletter,)).fetchall()
        return city

    def getcityimg(self, name):
        cityimg = self.cur.execute('SELECT picid FROM city WHERE name == ?', (name,)).fetchall()
        print(cityimg)
        return cityimg[0][0]

    def setcityindb(self, id, name):
        self.cur.execute("SELECT path FROM game WHERE tgid = ?", (id,))
        data = self.cur.fetchall()
        if len(data) == 0:
            self.cur.execute('INSERT INTO game(tgid, path, move) VALUES (?, ?, ?)', (id, "", 0))
            self.base.commit()
        else:
            pass
        path_old = self.cur.execute('SELECT path FROM game WHERE tgid == ?', (id,)).fetchall()[0][0]
        move_old = self.cur.execute('SELECT move FROM game WHERE tgid == ?', (id,)).fetchall()[0][0]
        move = 0
        path = str(path_old) + "->" + str(name)
        if move_old == 0:
            move = 1
        self.cur.execute('UPDATE game SET path == ? where tgid == ?;', (path, id))
        self.cur.execute('UPDATE game SET move == ? where tgid == ?;', (move, id))
        self.base.commit()

    def getlastcity(self, id):
        cities = self.cur.execute('SELECT path FROM game WHERE tgid == ?', (id,)).fetchall()[0][0]
        cities_arr = cities.split('-> ')
        if len(cities_arr) == 1:
            return cities_arr[0]
        return cities_arr[len(cities_arr) - 1]

    def returnmove(self, id):
        move = self.cur.execute('SELECT move FROM game WHERE tgid == ?', (id,)).fetchall()[0][0]
        return move

    def rndcity(self, id, last_letter):
        path = str(self.cur.execute('SELECT path FROM game WHERE tgid == ?', (id,)).fetchall()[0][0])
        cities = self.cur.execute('SELECT name FROM city WHERE firstletter == ?', (last_letter,)).fetchall()
        right = []
        for i in range(len(cities)):
            right.append(cities[i][0])
        for city in right:
            if path.find(city) == -1:
                return city
        return "$sudo -"
