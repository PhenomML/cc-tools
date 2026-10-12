#!/usr/bin/env python3
"""Check cross-session messages in a Claude Code transcript against the locator rule.

usage: check_message_locators.py <transcript.jsonl>

Reads received <cross-session-message> blocks and SendMessage tool inputs. A message passes when every
line is `<absolute path>[ § <heading>] @ <hash>`, the file exists, and the hash contains that path in the
file's own git repository. A line without a hash reports `no-hash` (expected for process locators).
"""
import json, os, re, subprocess, sys

RECV = re.compile(r'<cross-session-message from="[^"]*" from-name="([^"]*)"[^>]*>(.*?)</cross-session-message>', re.S)
LINE = re.compile(r'^(/.+?)(?: § (.+?))?(?: @ ?([0-9a-f]{7,40}))?$')

def walk(o):
    yield o
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)

def git(path, *args):
    return subprocess.run(['git', '-C', os.path.dirname(path) or '.', *args], capture_output=True, text=True)

def check_line(line):
    m = LINE.match(line.strip())
    if not m: return 'fail: not a locator'
    path, _, h = m.groups()
    if not os.path.isfile(path): return 'fail: file not found'
    top = git(path, 'rev-parse', '--show-toplevel')
    if top.returncode: return 'fail: not in a git repository' if h else 'no-hash (untracked)'
    if not h: return 'no-hash'
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(top.stdout.strip()))
    return 'PASS' if git(path, 'cat-file', '-e', f'{h}:{rel}').returncode == 0 else 'fail: hash does not contain this path'

def check(body):
    results = [check_line(l) for l in body.strip().splitlines() if l.strip()]
    return 'PASS' if results and all(r == 'PASS' for r in results) else '; '.join(sorted(set(results))) or 'fail: empty'

seen = set()
for line in open(sys.argv[1]):
    try: o = json.loads(line)
    except ValueError: continue
    for d in walk(o):
        if isinstance(d, str):
            for m in RECV.finditer(d):
                b = m.group(2).strip()
                if ('in', b) not in seen: seen.add(('in', b)); print('received', m.group(1), check(b), '|', b.splitlines()[0][:60])
        elif isinstance(d, dict) and d.get('name') == 'SendMessage' and isinstance(d.get('input'), dict):
            b = d['input'].get('message', '').strip()
            if ('out', b) not in seen: seen.add(('out', b)); print('sent', d['input'].get('to'), check(b), '|', b.splitlines()[0][:60])
