#!/usr/bin/env python3
# run_l2.py -- L2 HSQLDB smoke test runner. Growth-10 QA.
# Usage (from repo root): python tests/ddl/run_l2.py
# Requires: Java 11+, HSQLDB 2.x in ~/.m2/repository/org/hsqldb/hsqldb
import subprocess, sys, pathlib, shutil
REPO = pathlib.Path(__file__).resolve().parents[2]
SRC  = REPO / "tests/ddl/L2HsqldbSmokeTest.java"
OUT  = REPO / "tests/ddl/out"
LIB  = REPO / "tests/ddl/lib"
RAW  = REPO / "presets/ddl/build/hsqldb-schema.sql"
M2   = pathlib.Path.home() / ".m2/repository/org/hsqldb/hsqldb"
jars = sorted([p for p in M2.rglob("hsqldb-*.jar") if "sources" not in str(p) and "tests" not in str(p)])
if not jars: sys.exit("HSQLDB jar not found in ~/.m2 — install via mvn dependency:get -Dartifact=org.hsqldb:hsqldb:2.7.4")
JAR = jars[-1]
print(f"HSQLDB jar : {JAR}")
# Step 1: Regenerate raw schema
print("Step 1: Generating schema...")
(REPO / "presets/ddl/build").mkdir(exist_ok=True)
r = subprocess.run([sys.executable, str(REPO/"presets/ddl/render.py"), "--dialect", "hsqldb"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=str(REPO))
if r.returncode != 0: sys.exit("render.py failed")
RAW.write_text(r.stdout, encoding="utf-8")
print(f"  {len(r.stdout.splitlines())} lines")
# Step 2: Generate patched schema
print("Step 2: Patching schema (3 renderer defect workarounds)...")
r = subprocess.run([sys.executable, str(REPO/"tests/ddl/patch_schema.py"), str(RAW)],
    cwd=str(REPO), capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode != 0: sys.exit(f"patch_schema.py failed: {r.stderr}")
# Step 3: Compile
OUT.mkdir(exist_ok=True); LIB.mkdir(exist_ok=True)
jd = LIB / JAR.name
if not jd.exists(): shutil.copy(str(JAR), str(jd))
CP = str(jd) + ";" + str(OUT)
print("Step 3: Compiling...")
r = subprocess.run(["javac", "-cp", CP, str(SRC), "-d", str(OUT)], capture_output=True, text=True)
if r.returncode != 0: sys.exit("Compile failed: "+r.stderr)
print("  OK")
# Step 4: Run
print("Step 4: Running L2 smoke test..."+chr(10))
r = subprocess.run(["java", "-cp", CP, "L2HsqldbSmokeTest", str(RAW)], cwd=str(REPO))
sys.exit(r.returncode)
