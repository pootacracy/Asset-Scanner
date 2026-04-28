#!/usr/bin/env python3
"""Find executables in PATH and run -h (with --help fallback).
Saves outputs to CSV and per-command .txt files.
"""
import argparse
import csv
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def find_executables(path_env=None):
    path_env = path_env if path_env is not None else os.environ.get("PATH", "")
    dirs = [d for d in path_env.split(os.pathsep) if d]
    seen = set()
    results = []
    for d in dirs:
        try:
            with os.scandir(d) as it:
                for entry in it:
                    try:
                        if not entry.is_file(follow_symlinks=False):
                            continue
                        p = entry.path
                        if os.access(p, os.X_OK):
                            if p not in seen:
                                seen.add(p)
                                results.append(p)
                    except PermissionError:
                        continue
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
    results.sort()
    return results


def safe_name(p: str):
    name = os.path.basename(p)
    # replace problematic chars
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)


def run_help(path, timeout=5, try_fallback=True):
    tried = []
    def _run(opt):
        cmd = [path, opt]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=timeout)
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 'timeout', '', ''
        except Exception as e:
            return f'err:{type(e).__name__}', '', str(e)

    def _looks_like_invalid_option(text: str):
        if not text:
            return False
        s = text.lower()
        phrases = [
            'unrecognized option', 'unknown option', 'invalid option', 'illegal option',
            'unrecognized argument', 'invalid argument', 'unknown flag', 'invalid flag'
        ]
        return any(p in s for p in phrases)

    # Prefer --help first (safer). Only try -h if --help produced no useful output
    rc_help, out_help, err_help = _run('--help')
    tried.append('--help')
    rc, out, err = rc_help, out_help, err_help

    help_has_output = bool((out_help or err_help) and not _looks_like_invalid_option(out_help + '\n' + err_help))

    if not help_has_output and try_fallback:
        rc_h, out_h, err_h = _run('-h')
        tried.append('-h')
        # If -h appears to be an invalid option message, mark as unsupported and keep --help result
        if _looks_like_invalid_option(out_h + '\n' + err_h):
            # Do not treat unsupported -h as a failure; record that -h was unsupported
            rc = f'unsupported:-h'
            out = ''
            err = ''
        else:
            # prefer non-empty outputs from -h if present
            if out_h.strip() or err_h.strip():
                rc, out, err = rc_h, out_h, err_h
    return {
        'path': path,
        'name': os.path.basename(path),
        'tried': '|'.join(tried),
        'returncode': rc,
        'stdout': out,
        'stderr': err,
    }


def write_outputs(records, out_dir: Path, csv_path: Path, failures_csv_path: Path = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=['name','path','tried','returncode','stdout_file','stderr_file'])
        writer.writeheader()
        # track failures for separate CSV
        failures = []
        for r in records:
            base = f"{safe_name(r['name'])}"
            i = 0
            candidate = base
            while (out_dir / (candidate + '.stdout.txt')).exists() or (out_dir / (candidate + '.stderr.txt')).exists():
                i += 1
                candidate = f"{base}_{i}"
            stdout_file = out_dir / (candidate + '.stdout.txt')
            stderr_file = out_dir / (candidate + '.stderr.txt')
            try:
                stdout_file.write_text(r['stdout'] or '', encoding='utf-8')
            except Exception:
                stdout_file.write_text('', encoding='utf-8', errors='replace')
            try:
                stderr_file.write_text(r['stderr'] or '', encoding='utf-8')
            except Exception:
                stderr_file.write_text('', encoding='utf-8', errors='replace')
            writer.writerow({
                'name': r['name'],
                'path': r['path'],
                'tried': r['tried'],
                'returncode': r['returncode'],
                'stdout_file': str(stdout_file),
                'stderr_file': str(stderr_file),
            })

            # Determine failure criteria:
            # - timeout
            # - execution error (returncode like 'err:...')
            # - non-zero numeric returncode with no output
            rc = r.get('returncode')
            stdout = (r.get('stdout') or '')
            stderr = (r.get('stderr') or '')
            reason = None
            if rc == 'timeout':
                reason = 'timeout'
            elif isinstance(rc, str) and rc.startswith('err:'):
                reason = rc
            else:
                try:
                    if isinstance(rc, int) and rc != 0 and not (stdout.strip() or stderr.strip()):
                        reason = f'nonzero_no_output:{rc}'
                except Exception:
                    pass

            if reason:
                failures.append({
                    'name': r['name'],
                    'path': r['path'],
                    'tried': r['tried'],
                    'returncode': rc,
                    'reason': reason,
                    'stdout_file': str(stdout_file),
                    'stderr_file': str(stderr_file),
                })

    # write failures CSV if any
    if failures:
        if failures_csv_path is None:
            failures_csv_path = csv_path.parent / (csv_path.stem + '_failures.csv')
        try:
            with open(failures_csv_path, 'w', newline='', encoding='utf-8') as ff:
                fwriter = csv.DictWriter(ff, fieldnames=['name','path','tried','returncode','reason','stdout_file','stderr_file'])
                fwriter.writeheader()
                for f in failures:
                    fwriter.writerow(f)
        except Exception:
            pass


def parse_selection(text, max_index):
    # supports comma separated, ranges like 1-5
    out = set()
    for part in text.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            try:
                a = int(a); b = int(b)
                for i in range(max(1,a), min(max_index, b) + 1):
                    out.add(i-1)
            except Exception:
                continue
        else:
            try:
                i = int(part)
                if 1 <= i <= max_index:
                    out.add(i-1)
            except Exception:
                continue
    return sorted(out)


def main():
    p = argparse.ArgumentParser(description='Find executables in PATH and run -h/--help')
    p.add_argument('--timeout', type=float, default=5.0)
    p.add_argument('--workers', type=int, default=16)
    p.add_argument('--out-dir', default='help_outputs')
    p.add_argument('--csv', default='help_index.csv')
    p.add_argument('--fail-csv', default=None, help='path to failures CSV (optional)')
    p.add_argument('--filter', default=None, help='substring filter on executable path or name')
    p.add_argument('--interactive', action='store_true')
    p.add_argument('--no-fallback', dest='fallback', action='store_false')
    p.add_argument('--limit', type=int, default=0, help='limit number of commands (0 = no limit)')
    args = p.parse_args()

    exe_list = find_executables()
    if args.filter:
        exe_list = [x for x in exe_list if args.filter in x or args.filter in os.path.basename(x)]
    if args.limit and args.limit > 0:
        exe_list = exe_list[:args.limit]

    if not exe_list:
        print('No executables found in PATH')
        return

    if args.interactive:
        for i, e in enumerate(exe_list, start=1):
            print(f"{i:4}: {e}")
        sel = input('Enter selections (comma, ranges like 1-5). Enter ALL for everything: ').strip()
        if sel.upper() == 'ALL':
            indices = list(range(len(exe_list)))
        else:
            indices = parse_selection(sel, len(exe_list))
        exe_list = [exe_list[i] for i in indices]

    print(f'Running help for {len(exe_list)} executables with timeout={args.timeout}s')

    records = []
    out_dir = Path(args.out_dir)
    csv_path = Path(args.csv)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(run_help, path, timeout=args.timeout, try_fallback=args.fallback): path for path in exe_list}
        for fut in as_completed(futures):
            try:
                r = fut.result()
            except Exception as e:
                path = futures[fut]
                r = {'path': path, 'name': os.path.basename(path), 'tried': '', 'returncode': f'err:{type(e).__name__}', 'stdout': '', 'stderr': str(e)}
            records.append(r)

    failures_csv_path = Path(args.fail_csv) if args.fail_csv else None
    write_outputs(records, out_dir, csv_path, failures_csv_path)
    print('Done. CSV index:', csv_path)
    print('Raw outputs in:', out_dir)

if __name__ == '__main__':
    main()
