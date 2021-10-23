import pythonEsn

pythonEsn.start_esn(("39.100.5.139", 3003))
pythonEsn.login_esn("root", "turtle")
pythonEsn.request_recent(100000)