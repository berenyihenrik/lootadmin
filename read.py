import csv
from sqlalchemy import text
from database import *
from validate import *

def readcsv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = []
        for row in reader:
            rows.append(row)

        dates = []
        for i in range(1, len(rows)):
            if rows[i][1] not in dates:
                dates.append(rows[i][1])
        # print(dates)

        characters = []
        character = []
        for i in range(1, len(rows)):
            if arrayContains(rows[i][0], characters):
                character.append(rows[i][0])
                # character.append(rows[i][1])
                for j in range(len(dates)):
                    character.append([])

                character[dates.index(rows[i][1])+1].append(rows[i][5])

                characters.append(character)
                character = []
            else:
                for j in range(len(characters)):
                    if characters[j][0] == rows[i][0]:
                        characters[j][dates.index(rows[i][1])+1].append(rows[i][5])


        # print(characters)
        file.close()
        return characters, dates

def readrawcsv(stringio, tableid = None):
    reader = csv.reader(stringio)
    rows = []
    for row in reader:
        rows.append(row)

    dates = []
    for i in range(1, len(rows)):
        if rows[i][1] not in dates:
            dates.append(rows[i][1])

    characters = []
    character = []
    for i in range(1, len(rows)):
        if arrayContains(rows[i][0], characters):
            character.append(rows[i][0])
            for j in range(len(dates)):
                character.append([])

            character[dates.index(rows[i][1]) + 1].append(rows[i][5])

            characters.append(character)
            character = []
        else:
            for j in range(len(characters)):
                if characters[j][0] == rows[i][0]:
                    characters[j][dates.index(rows[i][1]) + 1].append(rows[i][5])

    if tableid is None:
        table = lootTables_db.query.order_by(text("loot_tables_db.tableid DESC")).first()
        tableid = table.tableid
    print(tableid)

    for i in range(1, len(rows)):

        loot = loot_db(tableid, rows[i][0], rows[i][1], rows[i][5])
        db.session.add(loot)
    db.session.commit()

    # return characters, dates

def readDB(tableid):
    rows = []
    row = []
    loot = loot_db.query.filter_by(tableid=tableid).all()
    for i in range(len(loot)):
        row.append(loot[i].character)
        row.append(loot[i].date)
        row.append(loot[i].itemid)
        rows.append(row)
        row = []

    dates = []
    for i in range(len(rows)):
        if rows[i][1] not in dates:
            dates.append(rows[i][1])

    characters = []
    character = []
    for i in range(len(rows)):
        if arrayContains(rows[i][0], characters):
            character.append(rows[i][0])
            for j in range(len(dates)):
                character.append([])

            character[dates.index(rows[i][1]) + 1].append(rows[i][2])

            characters.append(character)
            character = []
        else:
            for j in range(len(characters)):
                if characters[j][0] == rows[i][0]:
                    characters[j][dates.index(rows[i][1]) + 1].append(rows[i][2])
    return characters, dates