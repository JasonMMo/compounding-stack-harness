---
name: research:wiki-save
description: 리서치 결과를 knowledge/wiki에 저장하고 git 커밋한다 — 모든 리서치 세션 종료 전 필수. research-loop Step 6(wiki 환류) 단계. out/analysis/ 초안도 여기서 wiki로 이전.
argument-hint: <slug> <category: market|design|tech|concepts>
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

<objective>
리서치 내용을 knowledge/wiki/<category>/<slug>.md 에 저장하고
knowledge/wiki/index.md 에 1줄 포인터를 추가한 뒤 git 커밋한다.
</objective>

<process>

1. **인자 파싱**
   - `$ARGUMENTS` → `<slug>` (첫 토큰), `<category>` (두 번째 토큰)
   - 카테고리: `market` / `design` / `tech` / `concepts`
   - 인자 없으면: 현재 대화 컨텍스트에서 주제와 카테고리를 추론

2. **출력 경로 결정**
   ```
   knowledge/wiki/<category>/<slug>.md
   ```

3. **wiki 파일 작성 (신규 또는 업데이트)**
   프론트매터 포함:
   ```markdown
   ---
   slug: <slug>
   type: SYNTHESIZED | EXTRACTED | INFERRED
   updated: <오늘 날짜 YYYY-MM-DD>
   sources: <출처>
   related: <연관 파일>
   ---

   # <제목>

   <리서치 내용>
   ```
   - 기존 파일 있으면: Read 후 Edit으로 업데이트 (덮어쓰기 금지, 섹션 추가/갱신)

4. **index.md 업데이트**
   `knowledge/wiki/index.md`의 해당 카테고리 섹션에 1줄 추가:
   ```markdown
   - [<slug>](<category>/<slug>.md) — <1줄 요약> (updated: <날짜>) `[<type>]`
   ```
   - 이미 있으면 날짜·요약 갱신

5. **git 커밋 (2건)**
   ```bash
   git add knowledge/wiki/<category>/<slug>.md
   git commit -m "$(cat <<'EOF'
   docs(wiki): <slug> — <1줄 요약>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   EOF
   )"

   git add knowledge/wiki/index.md
   git commit -m "$(cat <<'EOF'
   docs(wiki/index): <slug> 포인터 추가

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

6. **결과 출력**
   ```
   wiki 저장 완료:
   - 파일: knowledge/wiki/<category>/<slug>.md
   - 커밋: 2건
   - 다음: /clear → 구현 세션 시작 (wiki만 참조)
   ```

</process>

<notes>
- out/analysis/ 초안이 있으면 내용을 wiki로 이전 후 out/ 파일은 유지 (gitignored)
- type 선택: SYNTHESIZED(여러 출처 통합) / EXTRACTED(단일 출처 추출) / INFERRED(추론)
- 커밋 메시지 Co-Authored-By는 현재 세션 모델로 업데이트 (growth 번호 참조)
</notes>
