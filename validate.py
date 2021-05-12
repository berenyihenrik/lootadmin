def arrayContains(item, array):
    for i in range(len(array)):
        if item in array[i]:
            return False
    return True

def checkLogin(request, users):
    if 'id' in request.cookies and request.cookies['id'] in users:
        return True
    return False
