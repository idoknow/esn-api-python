import ESNSession

ESNSession.debugMode = True
ESNSession.connect(("39.100.5.139", 3003))
ESNSession.login("root", "turtle")
ESNSession.requestRecent(100000)
