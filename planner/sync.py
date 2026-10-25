"""
Pull the latest version of planned runs down from the web planner.

The planner keeps each saved run in Firestore, at runs/<owner>/items/<name>,
and builds the .py in the browser by running PythFinder's own build_run. So
this does the same thing from the laptop: read the saved run, build it with
a local PythFinder checkout, and write the module where planner/sync.json
says it goes -- plus the planner's own .json copy into planner/, the same
file Export .json would give you.

    python3 planner/sync.py pull [file.py ...]   every mapped run, or just these
    python3 planner/sync.py runs [owner]         what is saved on the planner
    python3 planner/sync.py map file.py owner [name]

The justfile wraps these as `just pull`, `just runs` and `just map`.

The planner's Firebase project id and API key go in planner/credentials.json,
which git ignores -- {"project": "...", "api_key": "..."}, copied from
PythFinder's web/src/firebase.ts.

The build only matches the site if ~/PythFinder is on the same version the
site is running, so `git pull` there first if the output looks off.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAPPING = HERE / "sync.json"
CREDENTIALS = HERE / "credentials.json"

FIRESTORE = "https://firestore.googleapis.com/v1/projects/{0}/databases/(default)/documents"


# --- the mapping file ---------------------------------------------------------
def load_mapping() -> dict:
    if not MAPPING.exists():
        return {"pythfinder": "~/PythFinder", "runs": {}}

    return json.loads(MAPPING.read_text())


def save_mapping(mapping: dict):
    MAPPING.write_text(json.dumps(mapping, indent=2) + "\n")


# --- the credentials file -----------------------------------------------------
# The key is no secret -- the planner page ships it, and access is
# firestore.rules' job -- but the project id gives away the planner's unlisted
# address, and this repo is public. So both live in an ignored file.
def load_credentials() -> tuple:
    """The Firestore documents URL and the API key."""
    if not CREDENTIALS.exists():
        sys.exit("no {0} -- write {{\"project\": \"...\", \"api_key\": \"...\"}} there, "
                 "from PythFinder's web/src/firebase.ts".format(CREDENTIALS.relative_to(ROOT)))

    credentials = json.loads(CREDENTIALS.read_text())
    return FIRESTORE.format(credentials["project"]), credentials["api_key"]


# --- Firestore over REST ------------------------------------------------------
def decode(value: dict):
    """One Firestore REST value back into plain JSON."""
    if "mapValue" in value:
        fields = value["mapValue"].get("fields", {})
        return {key: decode(inner) for key, inner in fields.items()}

    if "arrayValue" in value:
        return [decode(inner) for inner in value["arrayValue"].get("values", [])]

    if "integerValue" in value:
        return int(value["integerValue"])

    if "nullValue" in value:
        return None

    # stringValue, doubleValue, booleanValue, timestampValue
    return next(iter(value.values()))


def request(url: str, body: dict = None):
    data = None if body is None else json.dumps(body).encode()
    headers = {} if body is None else {"Content-Type": "application/json"}

    with urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=20) as response:
        return json.load(response)


def fetch_run(owner: str, name: str):
    """The saved document -- {owner, name, savedAt, run} -- or None."""
    firestore, api_key = load_credentials()
    path = "runs/{0}/items/{1}".format(urllib.parse.quote(owner, safe=""),
                                       urllib.parse.quote(name, safe=""))

    try:
        document = request("{0}/{1}?key={2}".format(firestore, path, api_key))
    except urllib.error.HTTPError as problem:
        if problem.code == 404:
            return None
        raise

    return decode({"mapValue": document})


def list_runs(owner: str = None) -> list:
    """Every saved run, or one owner's, as (owner, name, savedAt)."""
    firestore, api_key = load_credentials()

    if owner is None:
        source = {"collectionId": "items", "allDescendants": True}
        parent = firestore
    else:
        source = {"collectionId": "items"}
        parent = "{0}/runs/{1}".format(firestore, urllib.parse.quote(owner, safe=""))

    query = {"structuredQuery": {
        "from": [source],
        "select": {"fields": [{"fieldPath": "owner"}, {"fieldPath": "name"},
                              {"fieldPath": "savedAt"}]},
    }}

    found = []
    for entry in request("{0}:runQuery?key={1}".format(parent, api_key), query):
        if "document" in entry:
            stored = decode({"mapValue": entry["document"]})
            found.append((stored.get("owner", "?"), stored.get("name", "?"), stored.get("savedAt", "?")))

    return sorted(found)


# --- building the .py ---------------------------------------------------------
def load_builder(mapping: dict):
    checkout = Path(os.environ.get("PYTHFINDER", mapping.get("pythfinder", "~/PythFinder"))).expanduser()

    if not (checkout / "pythfinder" / "headless.py").exists():
        sys.exit("no PythFinder checkout at {0} -- set \"pythfinder\" in {1}, or PYTHFINDER"
                 .format(checkout, MAPPING.relative_to(ROOT)))

    sys.path.insert(0, str(checkout))
    from pythfinder.headless import build_run

    return build_run


def show_diagnostics(result: dict):
    for diagnostic in result.get("diagnostics") or []:
        if isinstance(diagnostic, dict):
            line = "{0}: {1}".format(diagnostic.get("level", "note"), diagnostic.get("message", diagnostic))
            if diagnostic.get("suggestion"):
                line += " ({0})".format(diagnostic["suggestion"])
        else:
            line = str(diagnostic)

        print("    " + line)


def pull(mapping: dict, only: list) -> bool:
    runs = mapping.get("runs", {})
    targets = only or sorted(runs)

    if not targets:
        print("nothing mapped yet -- `just runs` to see what is saved, then `just map file.py owner name`")
        return True

    unknown = [target for target in targets if target not in runs]
    if unknown:
        sys.exit("not in {0}: {1}".format(MAPPING.relative_to(ROOT), ", ".join(unknown)))

    build_run = load_builder(mapping)
    all_ok = True

    for target in targets:
        source = runs[target]
        owner, name = source["owner"], source.get("name", Path(target).stem)
        print("{0}  <-  {1}/{2}".format(target, owner, name))

        stored = fetch_run(owner, name)
        if stored is None:
            print("    no saved run by that owner and name on the planner")
            all_ok = False
            continue

        result = build_run(stored["run"])
        show_diagnostics(result)

        module_text = result.get("module_text")
        if not module_text:
            print("    the planner could not build this run -- left the old file alone")
            all_ok = False
            continue

        module_path = ROOT / target
        plan_path = HERE / (Path(target).stem + ".json")
        plan_text = json.dumps(stored["run"], indent=2) + "\n"

        changed = False
        for path, text in ((module_path, module_text), (plan_path, plan_text)):
            if not path.exists() or path.read_text() != text:
                path.write_text(text)
                changed = True

        print("    {0} (saved {1})".format("updated" if changed else "already up to date",
                                         stored.get("savedAt", "?")))

    return all_ok


# --- command line -------------------------------------------------------------
def main(argv: list) -> int:
    mapping = load_mapping()
    command, args = (argv[0], argv[1:]) if argv else ("pull", [])

    if command == "pull":
        return 0 if pull(mapping, args) else 1

    if command == "runs":
        for owner, name, saved in list_runs(args[0] if args else None):
            print("{0:<16} {1:<24} {2}".format(owner, name, saved))
        return 0

    if command == "map" and len(args) in (2, 3):
        target, owner = args[0], args[1]
        name = args[2] if len(args) == 3 else Path(target).stem
        mapping.setdefault("runs", {})[target] = {"owner": owner, "name": name}
        save_mapping(mapping)
        print("{0}  <-  {1}/{2}".format(target, owner, name))
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
