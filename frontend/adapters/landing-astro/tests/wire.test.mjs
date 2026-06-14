/**
 * wire.test.mjs — Contract codegen + DEC-5 wire schema tests.
 * Verifies codegen.mjs emits correct entity.create types and endpoint map.
 * G-1: confirms no contract reimplementation in adapter.
 *
 * Run: node --test tests/wire.test.mjs
 */

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ADAPTER_ROOT = resolve(__dirname, '..')
const SCRIPT = resolve(ADAPTER_ROOT, 'scripts', 'codegen.mjs')
const GEN_OUT = resolve(ADAPTER_ROOT, 'src', 'lib', 'contract.gen.ts')

function runCodegen() {
  return execFileSync(process.execPath, [SCRIPT], {
    cwd: ADAPTER_ROOT,
    encoding: 'utf8',
  })
}

test('codegen: exits 0', () => {
  const out = runCodegen()
  assert.ok(out.includes('[codegen] Wrote'), 'must print Wrote path')
})

test('codegen: emits contract.gen.ts', () => {
  runCodegen()
  assert.ok(existsSync(GEN_OUT), 'contract.gen.ts must be created')
})

test('codegen: contains WIRE_VERSION constant', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes('WIRE_VERSION'), 'must export WIRE_VERSION')
})

test('codegen: contains ENDPOINT_MAP with entity_create key', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes('entity_create'), 'ENDPOINT_MAP must contain entity_create key')
  assert.ok(src.includes('/api/entities/:entity_type'), 'entity_create must map to /api/entities/:entity_type')
})

test('codegen: DEC-5 — contains LeadData interface', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes('LeadData'), 'must export LeadData interface')
  assert.ok(src.includes('name: string'), 'LeadData must have name field')
  assert.ok(src.includes('email: string'), 'LeadData must have email field')
  assert.ok(src.includes('message: string'), 'LeadData must have message field')
})

test('codegen: DEC-5 — contains LEAD_ENTITY_TYPE constant', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes("LEAD_ENTITY_TYPE = 'lead'"), 'must export LEAD_ENTITY_TYPE = "lead"')
})

test('codegen: DEC-5 — EntityCreateRequest interface present', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes('EntityCreateRequest'), 'must export EntityCreateRequest interface')
  assert.ok(src.includes('entity_type: string'), 'EntityCreateRequest must have entity_type field')
  assert.ok(src.includes('data: Record'), 'EntityCreateRequest must have data field')
})

test('codegen: G-1 — generated file has GENERATED header comment', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.startsWith('// GENERATED'), 'generated file must start with GENERATED comment')
})

test('codegen: contains ERROR_CODES catalog', () => {
  runCodegen()
  const src = readFileSync(GEN_OUT, 'utf8')
  assert.ok(src.includes('ERROR_CODES'), 'must contain ERROR_CODES catalog')
})
