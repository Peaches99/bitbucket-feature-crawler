from curses.ascii import isspace
from util.model import Project, Feature, Scenario

def concatEx(input, excluded):
    s = ""
    arr = tokenize(input)
    for s1 in arr:
        if s1 != excluded:
            s += s1 + " "
    return s

def concat(input):
    s = ""
    arr = tokenize(input)
    for s1 in arr:
        s += s1 + " "
    return s

def buildScenario(arr):
    return Scenario(
            concatEx(arr[0], "Scenario:"),
            concat(arr[1]),
            concat(arr[2]),
            concat(arr[3])
    )

def tokenize(s):
    arr = []
    stringTokenizer = s.split()
    for i in stringTokenizer:
        arr.append(i)
    return arr

def buildFeature(lines):
    featureName = ""
    description = ""
    isDescription = False
    scenarios = []
    tokens = []

    for line in lines:
        
        if len(line) == 0 or line.isspace():
            continue

        tokens = tokenize(line)
        
        if tokens[0] == "Given" or tokens[0] == "When"  or  tokens[0] == "Then":
            continue

        if tokens[0] == "Feature:":
            
            featureName = concatEx(line, "Feature:")
            isDescription = True
        elif tokens[0] == "Scenario:":
            scenarios.append(buildScenario(lines[lines.index(line):lines.index(line) + 4]))
            isDescription = False

        if lines.index(line) > 0 and isDescription:
            description += concat(line)

    return Feature(featureName, description, scenarios)

def buildProject(key, slug, files):
    features = []

    for lines in files:
        features.append(buildFeature(lines))

    return Project(key + ":" + slug, features)