import importlib, os, pickle

def loadLibrary(modulePath):
    modulePath = str(modulePath)
    if ".py" not in modulePath:
        raise Exception("Import .py file")

    moduleName = modulePath.split("/")[-1]
    modulePath = modulePath.replace(moduleName, "")
    moduleName = moduleName.replace(".py", '')

    os.sys.path.append(os.path.abspath(modulePath))
    # Do the import
    #msg = f"{modulePath}\n{os.path.abspath(modulePath)}\n{moduleName}"
    #npyscreen.notify_confirm(msg, "Entry Error")
    
    return importlib.import_module(moduleName)

def Serialize (obj, path, name, createFolder=True):
    try:
        os.mkdir(path)
    except:
        pass
    if createFolder:
        os.mkdir(f'{path}/{name}')
        path = f'{path}/{name}'
    binary_file = open(f'{path}/{name}.bin',mode='wb')
    pickle.dump(obj, binary_file)
    binary_file.close()

def Deserialize (path):
    binary_file = open(path,mode='rb')
    return pickle.load(binary_file)
