import pathlib, json
d = json.loads(pathlib.Path("data.json").read_text())  # fail loudly on bad JSON before publishing
t = pathlib.Path("template.html").read_text()
pathlib.Path("index.html").write_text(t.replace("__DATA__", json.dumps(d, ensure_ascii=False).replace("</", "<\\/")))
