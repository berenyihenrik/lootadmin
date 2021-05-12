import csv

def readcsv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = []
        for row in reader:
            rows.append(row)

        dates = []
        for i in range(1, len(rows)):
            if (rows[i][1] not in dates):
                dates.append(rows[i][1])
        # print(dates)

        characters = []
        character = []
        for i in range(1, len(rows)):
            if(arrayContains(rows[i][0], characters)):
                character.append(rows[i][0])
                # character.append(rows[i][1])
                for j in range(len(dates)):
                    character.append([])

                character[dates.index(rows[i][1])+1].append(rows[i][5])

                characters.append(character)
                character = []
            else:
                for j in range(len(characters)):
                    if(characters[j][0] == rows[i][0]):
                        characters[j][dates.index(rows[i][1])+1].append(rows[i][5])


        # print(characters)
        file.close()
        return characters, dates

def readrawcsv(stringio):
    reader = csv.reader(stringio)
    rows = []
    for row in reader:
        rows.append(row)

    dates = []
    for i in range(1, len(rows)):
        if (rows[i][1] not in dates):
            dates.append(rows[i][1])
    # print(dates)

    characters = []
    character = []
    for i in range(1, len(rows)):
        if (arrayContains(rows[i][0], characters)):
            character.append(rows[i][0])
            # character.append(rows[i][1])
            for j in range(len(dates)):
                character.append([])

            character[dates.index(rows[i][1]) + 1].append(rows[i][5])

            characters.append(character)
            character = []
        else:
            for j in range(len(characters)):
                if (characters[j][0] == rows[i][0]):
                    characters[j][dates.index(rows[i][1]) + 1].append(rows[i][5])

    # print(characters)
    return characters, dates

def arrayContains(item, array):
    for i in range(len(array)):
        if(item in array[i]):
            return False
    return True