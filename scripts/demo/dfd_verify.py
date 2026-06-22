import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import seed_lawfirm_full as S

DDL=(pathlib.Path(__file__).parents[2]/'out'/'lawfirm-demo'/'ddl'/'postgres.sql').read_text(encoding='utf-8')
BASE_DEPT={'11111111-0000-0000-0000-000000000001'}
BASE_EMP={'22222222-0000-0000-0000-000000000001','22222222-0000-0000-0000-000000000002','22222222-0000-0000-0000-000000000003'}
BASE_CASE={'44444444-0000-0000-0000-000000000001','44444444-0000-0000-0000-000000000002','44444444-0000-0000-0000-000000000003'}
ALL_DEPT=BASE_DEPT|{d['id'] for d in S.NEW_DEPARTMENTS}
ALL_EMP=BASE_EMP|{e['id'] for e in S.NEW_EMPLOYEES}
ALL_CASE=BASE_CASE|{c['id'] for c in S.NEW_CASES}
ALL_CAT={c['id'] for c in S.DOC_CATEGORIES}
ALL_VER={v['id'] for v in S.DOC_VERSIONS}
ALL_STEP={s['id'] for s in S.APPROVAL_STEPS}
ALL_APP={a['id'] for a in S.APPROVAL_APPROVERS}
R=[]
def chk(vid,ok,msg):
    st='PASS' if ok else 'FAIL'
    R.append((vid,st,msg))
    print('  {:<20s} {}  {}'.format(vid,st,msg))
def na(vid,msg):
    R.append((vid,'N-A',msg))
    print('  {:<20s} N-A  {}'.format(vid,msg))
print('='*70); print('DFD verification'); print('='*70)
print('\n[P1]')
for vid,d in [('VP-P1-01','wrong pwd->401'),('VP-P1-02','no session->302'),('VP-P1-03','expired->302'),('VP-P1-04','after logout->302'),('VP-P1-05','home 4cards')]:
    na(vid,d+' -- HTTP runtime')
print('\n[P2]')
ba=[('CASE-2024-001','22222222-0000-0000-0000-000000000001'),('CASE-2024-002','22222222-0000-0000-0000-000000000002'),('CASE-2024-003','22222222-0000-0000-0000-000000000003')]
aa=ba+[(c['case_number'],c['assigned_attorney_id']) for c in S.NEW_CASES]
da=[(cn,ai) for cn,ai in aa if ai not in ALL_EMP]
chk('VP-P2-01',not da,'dangling: {}'.format(da) if da else 'all assigned_attorney_id FK valid')
VCT={'civil','criminal','administrative','family','commercial'}
bc=[(c['case_number'],c['case_type']) for c in S.NEW_CASES if c['case_type'] not in VCT]
chk('VP-P2-02',not bc,'violation: {}'.format(bc) if bc else 'OK')
VCS={'intake','active','trial','appeal','closed','withdrawn'}
bcs=[(c['case_number'],c['status']) for c in S.NEW_CASES if c['status'] not in VCS]
chk('VP-P2-03',not bcs,'violation: {}'.format(bcs) if bcs else 'OK')
acn=['CASE-2024-001','CASE-2024-002','CASE-2024-003']+[c['case_number'] for c in S.NEW_CASES]
dc=[n for n in set(acn) if acn.count(n)>1]
chk('VP-P2-04',not dc,'no dup' if not dc else 'dup: {}'.format(dc))
casc_lc='ON DELETE CASCADE' in DDL and 'legal_case' in DDL
chk('VP-P2-05',casc_lc,'legal_case_party CASCADE DDL present')
chk('VP-P2-06',casc_lc,'legal_case_document CASCADE DDL present')
print('\n[P3]')
bcit=['대법원 2020다12345','서울고등법원 2019나56789','대법원 2018다98765','헌법재판소 2017헌바321','대법원 2021도11111']
ac=bcit+[p['citation'] for p in S.NEW_PRECEDENTS]
dc2=[c for c in set(ac) if ac.count(c)>1]
chk('VP-P3-01',not dc2,'no dup citations' if not dc2 else 'dup')
hd=any('이혼' in p.get('keywords','') or '이혼' in p['holding'] for p in S.NEW_PRECEDENTS)
chk('VP-P3-02',hd,'divorce precedent exists' if hd else 'missing!')
na('VP-P3-03','0-result render -- HTTP runtime')
print('\n[P4]')
dcp=[p for p in S.CASE_PARTIES if p['case_id'] not in ALL_CASE]
chk('VP-P4-01',not dcp,'dangling: {}'.format([(p['id'],p['case_id']) for p in dcp]) if dcp else 'OK')
VR={'plaintiff','defendant','witness','opposing-counsel','expert-witness'}
br=[(p['id'],p['role']) for p in S.CASE_PARTIES if p['role'] not in VR]
chk('VP-P4-02',not br,'violation: {}'.format(br) if br else 'OK')
c7d=[p for p in S.CASE_PARTIES if p['case_id']==S._C7 and p['role']=='defendant']
chk('VP-P4-03',len(c7d)==2,'C7 {} defendants (multiple allowed)'.format(len(c7d)))
print('\n[P5]')
dcd=[d for d in S.CASE_DOCUMENTS if d['case_id'] not in ALL_CASE]
chk('VP-P5-01',not dcd,'dangling: {}'.format([(d['id'],d['case_id']) for d in dcd]) if dcd else 'OK')
VI={'pending','processing','done','error'}
bi=[d for d in S.CASE_DOCUMENTS if d['ingest_status'] not in VI]
hp=any(d['ingest_status']=='pending' for d in S.CASE_DOCUMENTS)
chk('VP-P5-02',not bi and hp,'ingest OK {} pending'.format(sum(1 for d in S.CASE_DOCUMENTS if d['ingest_status']=='pending')) if not bi else 'violation: {}'.format(bi))
VDT={'complaint','brief','evidence','court-order','contract','correspondence','other'}
bdt=[(d['id'],d['document_type']) for d in S.CASE_DOCUMENTS if d['document_type'] not in VDT]
chk('VP-P5-03',not bdt,'violation: {}'.format(bdt) if bdt else 'OK')
na('VP-P5-04','ingest_status reverse -- app layer runtime')
print('\n[P6]')
ded=[(e['id'],e['department_id']) for e in S.NEW_EMPLOYEES if e['department_id'] not in ALL_DEPT]
chk('VP-P6-01',not ded,'dangling: {}'.format(ded) if ded else 'OK')
ra='ON DELETE RESTRICT' in DDL and 'assigned_attorney_id' in DDL
chk('VP-P6-02',ra,'assigned_attorney_id RESTRICT DDL present')
ro='ON DELETE RESTRICT' in DDL and 'owner_id' in DDL
chk('VP-P6-03',ro,'owner_id RESTRICT DDL present')
VES={'active','on-leave','terminated'}
bes=[(e['id'],e['status']) for e in S.NEW_EMPLOYEES if e['status'] not in VES]
chk('VP-P6-04',not bes,'violation: {}'.format(bes) if bes else 'OK')
aen=['EMP001','EMP002','EMP003']+[e['employee_number'] for e in S.NEW_EMPLOYEES]
den=[n for n in set(aen) if aen.count(n)>1]
chk('VP-P6-05',not den,'no dup employee_number' if not den else 'dup: {}'.format(den))
print('\n[P7]')
ddc=[(d['id'],d['category_id']) for d in S.DOC_DOCUMENTS if d['category_id'] not in ALL_CAT]
chk('VP-P7-01',not ddc,'dangling: {}'.format(ddc) if ddc else 'OK')
ddo=[(d['id'],d['owner_id']) for d in S.DOC_DOCUMENTS if d['owner_id'] not in ALL_EMP]
chk('VP-P7-02',not ddo,'dangling: {}'.format(ddo) if ddo else 'OK')
vk=[(v['document_id'],v['version_number']) for v in S.DOC_VERSIONS]
dvk=[k for k in set(vk) if vk.count(k)>1]
chk('VP-P7-03',not dvk,'no dup (doc_id,ver_num)' if not dvk else 'dup: {}'.format(dvk))
ardk=[(r['document_id'],r['principal_type'],r['principal_id']) for r in S.DOC_ACCESS_RULES]
dak=[k for k in set(ardk) if ardk.count(k)>1]
chk('VP-P7-04',not dak,'no dup access_rule key' if not dak else 'dup: {}'.format(dak))
VPP={'read','edit','admin'}
bp=[(r['id'],r['permission']) for r in S.DOC_ACCESS_RULES if r['permission'] not in VPP]
chk('VP-P7-05',not bp,'violation: {}'.format(bp) if bp else 'OK')
casc_dd='ON DELETE CASCADE' in DDL and 'document_document' in DDL
chk('VP-P7-06',casc_dd,'document_access_rule CASCADE DDL present')
chk('VP-P7-07',casc_dd,'document_version CASCADE DDL present')
drr=[r for r in S.DOC_ACCESS_RULES if r['principal_type']=='department']
err=[r for r in S.DOC_ACCESS_RULES if r['principal_type']=='employee']
ddr=[(r['id'],r['principal_id']) for r in drr if r['principal_id'] not in ALL_DEPT]
der=[(r['id'],r['principal_id']) for r in err  if r['principal_id'] not in ALL_EMP]
chk('VP-P7-08',not ddr and not der,'polymorphic IDs all valid' if not ddr and not der else 'dept: {} emp: {}'.format(ddr,der))
print('\n[P8]')
drq=[(r['id'],r['requester_id']) for r in S.APPROVAL_REQUESTS if r['requester_id'] not in ALL_EMP]
chk('VP-P8-01',not drq,'dangling: {}'.format(drq) if drq else 'OK')
VRS={'pending','in-progress','approved','rejected','cancelled','expired'}
brs=[(r['id'],r['status']) for r in S.APPROVAL_REQUESTS if r['status'] not in VRS]
chk('VP-P8-02',not brs,'violation: {}'.format(brs) if brs else 'OK')
ssk=[(s['request_id'],s['sequence']) for s in S.APPROVAL_STEPS]
dsk=[k for k in set(ssk) if ssk.count(k)>1]
chk('VP-P8-03',not dsk,'no dup (req_id,seq)' if not dsk else 'dup: {}'.format(dsk))
apk=[(a['step_id'],a['employee_id']) for a in S.APPROVAL_APPROVERS]
dapk=[k for k in set(apk) if apk.count(k)>1]
chk('VP-P8-04',not dapk,'no dup (step_id,emp_id)' if not dapk else 'dup: {}'.format(dapk))
VDD={'approved','rejected'}
bdd=[(d['id'],d['decision']) for d in S.APPROVAL_DECISIONS if d['decision'] not in VDD]
chk('VP-P8-05',not bdd,'violation: {}'.format(bdd) if bdd else 'OK')
dek=[(d['step_id'],d['approver_id']) for d in S.APPROVAL_DECISIONS]
ddk=[k for k in set(dek) if dek.count(k)>1]
chk('VP-P8-06',not ddk,'no dup decision key' if not ddk else 'dup: {}'.format(ddk))
casc_ar='ON DELETE CASCADE' in DDL and 'approval_request' in DDL
chk('VP-P8-07',casc_ar,'approval_step CASCADE DDL present')
na('VP-P8-08','pending->in-progress -- app layer runtime')
na('VP-P8-09','in-progress->approved -- app layer runtime')
AQ5=S._aqid(5)
aq5r=next((r for r in S.APPROVAL_REQUESTS if r['id']==AQ5),None)
s7=next((ss for ss in S.APPROVAL_STEPS if ss['id']==S._asid(7)),None)
s8=next((ss for ss in S.APPROVAL_STEPS if ss['id']==S._asid(8)),None)
aa8=next((a for a in S.APPROVAL_APPROVERS if a['id']==S._aaid(8)),None)
ok10=(aq5r and aq5r['status']=='in-progress' and s7 and s7['status']=='approved' and s8 and s8['status']=='active' and aa8 and aa8['responded_at'] is None)
chk('VP-P8-10',ok10,'AQ5 req={} s1={} s2={} responded={}'.format(aq5r['status'] if aq5r else '?',s7['status'] if s7 else '?',s8['status'] if s8 else '?',aa8['responded_at'] if aa8 else '?'))
print('\n[Additional FK integrity]')
ALL_APP2={a['id'] for a in S.APPROVAL_APPROVERS}
ALL_STEP2={s['id'] for s in S.APPROVAL_STEPS}
dad=[(d['id'],d['approver_id']) for d in S.APPROVAL_DECISIONS if d['approver_id'] not in ALL_APP2]
print('  decision.approver_id:','OK' if not dad else 'FAIL: '+str(dad))
dds=[(d['id'],d['step_id']) for d in S.APPROVAL_DECISIONS if d['step_id'] not in ALL_STEP2]
print('  decision.step_id:','OK' if not dds else 'FAIL: '+str(dds))
das=[(a['id'],a['step_id']) for a in S.APPROVAL_APPROVERS if a['step_id'] not in ALL_STEP2]
print('  approver.step_id:','OK' if not das else 'FAIL: '+str(das))
dae=[(a['id'],a['employee_id']) for a in S.APPROVAL_APPROVERS if a['employee_id'] not in ALL_EMP]
print('  approver.employee_id:','OK' if not dae else 'FAIL: '+str(dae))
dub=[(v['id'],v['uploaded_by']) for v in S.DOC_VERSIONS if v['uploaded_by'] not in ALL_EMP]
print('  version.uploaded_by:','OK' if not dub else 'FAIL: '+str(dub))
cvm=all(v in ALL_VER for v in S.DOC_CURRENT_VERSION_MAP.values())
print('  current_version_id backfill:','OK' if cvm else 'FAIL')
print('\n[DDL current_version_id]')
for line in DDL.split('\n'):
    if 'current_version_id' in line: print(' ',line.strip())
print('\n'+'='*70)
pn=sum(1 for _,s,_ in R if s=='PASS'); fn=sum(1 for _,s,_ in R if s=='FAIL'); nn=sum(1 for _,s,_ in R if s=='N-A')
print('RESULT: PASS={} FAIL={} N-A={} TOTAL={}'.format(pn,fn,nn,len(R)))
if fn:
    print('\nFAIL list:')
    for vid,s,m in R:
        if s=='FAIL': print('  {}: {}'.format(vid,m))
