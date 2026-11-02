#!/usr/bin/env bash
# POSIX (macOS / Linux) counterpart of build.bat.

set -u

fail() {
    echo "ERROR: Failure" >&2
    exit 1
}

echo "Clear up dist/..."
rm -rf dist
mkdir -p dist

echo "-"
echo "-"
echo "Update program version"
mkdir -p src/GENERATED
printf "%s\n" "'''For auto-generated files'''" > src/GENERATED/__init__.py
printf "%s\n" "# THIS IS AUTO-GENERATED" > src/GENERATED/_VERSION.py
python -c "from datetime import datetime; print(f'# {datetime.now()}')" >> src/GENERATED/_VERSION.py
python -c "import subprocess; v=subprocess.run(['git','describe','--tags','--dirty'],stdout=subprocess.PIPE).stdout.decode().strip(); print('_VERSION = '+repr(v))" >> src/GENERATED/_VERSION.py
echo "Done"

echo "Re-build html template"
python build_compiled_template.py
echo "Done"

echo "Calling pinliner..."
python src_dev_build/lib/pinliner/pinliner/pinliner.py src -o dist/mdmtoolsap_bundle.py || fail
echo "Done"

echo "Patching mdmtoolsap_bundle.py..."
cat >> dist/mdmtoolsap_bundle.py <<'EOF'
# ...
# print('within mdmtoolsap_bundle')
from src import launcher
launcher.main()
# print('out of mdmtoolsap_bundle')
EOF

echo "-"
echo "-"
echo "Bring LICENSE, README.md and requirements.txt to dist..."
if [ ! -f requirements.txt ]; then
    printf "%s\n" "# Runtime dependencies, one per line." > requirements.txt
fi
cp LICENSE dist/LICENSE
cp README.md dist/README.md
cp requirements.txt dist/requirements.txt
echo "Done"

echo "-"
echo "-"
echo "Copy and adapt run_init scripts to dist..."
sed -e 's#src/lib#optional_dependencies#g' run_init.sh > dist/run_init.sh
sed -e 's#src\\lib#optional_dependencies#g' run_init.bat > dist/run_init.bat
chmod +x dist/run_init.sh
chmod +x dist/run_init.bat
echo "Done"

echo "-"
echo "-"
echo "Verify the bundle: run --program done..."
python dist/mdmtoolsap_bundle.py --program done || fail
echo "Done"

echo "End"
