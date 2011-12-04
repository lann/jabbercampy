import glob, os, sys

vendor_paths = glob.glob(
    os.path.join(
        os.path.dirname(__file__), '..', 'vendor', '*', ''))

for path in vendor_paths:
    if path not in sys.path:
        sys.path.insert(0, path)
