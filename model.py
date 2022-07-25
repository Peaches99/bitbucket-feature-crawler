class Project:
    def __init__(self, projectID, features):
        self.projectID = projectID
        self.features = features

    def getProjectID(self):
        return self.projectID
    
    def getFeatures(self):
        return self.features

class Feature:
    def __init__(self, featureName, description, scenarios):
        self.featureName = featureName
        self.description = description
        self.scenarios = scenarios

    def getFeatureName(self):
        return self.featureName

    def getDescription(self):
        return self.description

    def getScenarios(self):
        return self.scenarios

class Scenario:
    def __init__(self, scenarioName, given, when, then):
        self.scenarioName = scenarioName
        self.given = given
        self.when = when
        self.then = then

    def getScenarioName(self):
        return self.scenarioName

    def getGiven(self):
        return self.given

    def getWhen(self):
        return self.when

    def getThen(self):
        return self.then

    