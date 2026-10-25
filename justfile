# Runs from the web planner -- the mapping lives in planner/sync.json.

# pull the latest of every mapped run, or just the files named
pull *files:
    python3 planner/sync.py pull {{files}}

# list the runs saved on the planner, everyone's or one owner's
runs owner="":
    python3 planner/sync.py runs {{owner}}

# remember that a local file comes from owner's saved run (name defaults to the file's)
map file owner name="":
    python3 planner/sync.py map {{file}} {{owner}} {{name}}
