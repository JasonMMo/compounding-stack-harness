#!/usr/bin/env python3
# patch_schema.py -- applies 3 HSQLDB renderer defect workarounds to generate a loadable test schema.
# Called by run_l2.py. Growth-10 QA.
import pathlib, re, sys

RAW = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("presets/ddl/build/hsqldb-schema.sql")
OUT = RAW.parent / (RAW.stem + "-patched.sql")
content = RAW.read_text(encoding="utf-8")

# Patch 1: Fix forward-FK
FK = '    FOREIGN KEY ("manager_id") REFERENCES "hr_employee" ("id") ON DELETE SET NULL'
IDX = 'CREATE INDEX "idx_hr_employee_status" ON "hr_employee" ("status");'
ALT = 'ALTER TABLE "hr_department" ADD FOREIGN KEY ("manager_id") REFERENCES "hr_employee" ("id") ON DELETE SET NULL;'
content = content.replace(FK+",\n", "").replace(FK+"\n", "")
content = content.replace(IDX, IDX+"\n"+ALT)
print("Patch 1 OK")

# Patch 2: Quote column names in explicit CHECK constraints
KW = {"IS","NULL","OR","AND","NOT","IN","TRUE","FALSE"}
def fix_check(m):
    expr = m.group(1)
    if expr.strip().startswith(chr(34)): return m.group(0)
    def qcol(t):
        tok = t.group(0)
        if tok.upper() in KW: return tok
        import re as _re
        if _re.match(r"[a-z][a-z0-9_]*$", tok): return chr(34)+tok+chr(34)
        return tok
    import re as _re
    return 'CHECK (' + _re.sub(r'\b([a-z][a-z0-9_]*)\b', qcol, expr) + ')'
content = re.sub(r"CHECK \(([^)]+)\)", fix_check, content)
print("Patch 2 OK")
# Patch 3: Fix DEFAULT placement (TYPE NOT NULL DEFAULT -> TYPE DEFAULT NOT NULL)
import re as _re2
lines_out = []
for line in content.splitlines():
    m = _re2.match(r'^'r'(\s+\"[^\"]+\" (?:BOOLEAN|INTEGER|DATE|TIMESTAMP|NUMERIC\([^)]+\)|VARCHAR\([^)]+\)|LONGVARCHAR)) NOT NULL DEFAULT (\S+?)(,?)$', line)
    if m: line = m.group(1)+" DEFAULT "+m.group(2)+" NOT NULL"+m.group(3)
    lines_out.append(line)
content = chr(10).join(lines_out)
print("Patch 3 OK")

OUT.write_text(content, encoding="utf-8")
print(f"Patched schema written: {OUT}")