import os

# import all views
for view in (x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x != "__init__.py"):
    __import__("%s" % view, globals(), locals(), [], -1)

