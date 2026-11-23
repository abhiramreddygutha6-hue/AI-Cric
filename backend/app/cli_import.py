"""Import Cricsheet JSON files.
Inside Docker:  docker compose exec backend python -m app.cli_import /data/cricsheet --limit 200
"""
import argparse
from app.database import Base, SessionLocal, engine
import app.models  # noqa: F401
from app.services.importer import import_folder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="folder with Cricsheet .json files")
    ap.add_argument("--limit", type=int, default=None, help="stop after N new matches")
    args = ap.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        stats = import_folder(db, args.folder, limit=args.limit)
    print(f"Done: {stats}")


if __name__ == "__main__":
    main()
