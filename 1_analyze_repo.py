import os, sys, ast, re, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SOURCE_EXT = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h',
              '.go', '.rb', '.php', '.ino', '.sql', '.gs'}
DOC_EXT = {'.md', '.txt', '.rst'}
CONFIG_EXT = {'.json', '.yml', '.yaml', '.toml', '.cfg', '.ini', '.xlsx', '.csv'}
ASSET_EXT = {'.png', '.jpg', '.jpeg', '.ico', '.svg', '.woff', '.ttf', '.pyc', '.gitignore'}
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.next'}

def classify(path):
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    if name.startswith('.env') or name in ('Dockerfile', 'docker-compose.yml', 'package-lock.json'):
        return 'config'
    if ext in SOURCE_EXT:
        return 'source'
    if ext in DOC_EXT or name.lower().startswith('readme'):
        return 'doc'
    if ext in CONFIG_EXT:
        return 'config'
    if ext in ASSET_EXT:
        return 'asset'
    return 'other'

def walk_repo(root):
    buckets = {'source': [], 'doc': [], 'config': [], 'asset': [], 'other': []}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            full = os.path.join(dirpath, f)
            buckets[classify(full)].append(full)
    return buckets

# ---------- Code Parser ----------
def parse_python(path):
    chunks = []
    try:
        src = open(path, encoding='utf-8', errors='ignore').read()
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', start + 1)
                text = "\n".join(lines[start:end])
                kind = 'class' if isinstance(node, ast.ClassDef) else 'function'
                chunks.append({'file': path, 'name': node.name, 'kind': kind,
                                'start': start + 1, 'end': end, 'text': text})
    except SyntaxError:
        pass
    return chunks

JS_FUNC_RE = re.compile(
    r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\(|'
    r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|'
    r'class\s+(\w+)'
)

def parse_js_like(path):
    chunks = []
    try:
        src = open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return chunks
    lines = src.splitlines()
    matches = list(JS_FUNC_RE.finditer(src))
    for i, m in enumerate(matches):
        name = next(g for g in m.groups() if g)
        start_line = src[:m.start()].count('\n')
        end_line = min(start_line + 25, len(lines))  # heuristic window
        text = "\n".join(lines[start_line:end_line])
        chunks.append({'file': path, 'name': name, 'kind': 'function/class',
                        'start': start_line + 1, 'end': end_line, 'text': text})
    return chunks

SQL_STMT_RE = re.compile(r'(CREATE[^;]+;|SELECT[^;]+;|INSERT[^;]+;|UPDATE[^;]+;)', re.I | re.S)

def parse_sql(path):
    chunks = []
    try:
        src = open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return chunks
    for i, m in enumerate(SQL_STMT_RE.finditer(src)):
        chunks.append({'file': path, 'name': f'statement_{i+1}', 'kind': 'sql',
                        'start': None, 'end': None, 'text': m.group(0)[:600]})
    if not chunks and src.strip():
        chunks.append({'file': path, 'name': 'full_file', 'kind': 'sql',
                        'start': None, 'end': None, 'text': src[:1200]})
    return chunks

def parse_ino(path):
    # Arduino .ino ~ C-like; reuse a simple function regex
    chunks = []
    try:
        src = open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return chunks
    lines = src.splitlines()
    for m in re.finditer(r'\b\w[\w\* ]*\s+(\w+)\s*\([^;{]*\)\s*\{', src):
        name = m.group(1)
        start_line = src[:m.start()].count('\n')
        end_line = min(start_line + 20, len(lines))
        chunks.append({'file': path, 'name': name, 'kind': 'function',
                        'start': start_line + 1, 'end': end_line,
                        'text': "\n".join(lines[start_line:end_line])})
    return chunks

def parse_source(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.py':
        return parse_python(path)
    if ext in ('.js', '.jsx', '.ts', '.tsx'):
        return parse_js_like(path)
    if ext == '.sql':
        return parse_sql(path)
    if ext == '.ino':
        return parse_ino(path)
    return []

# ---------- Text Parser (docs) ----------
def parse_doc(path):
    chunks = []
    try:
        src = open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return chunks
    sections = re.split(r'\n(?=#{1,3}\s)', src)
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        header_match = re.match(r'#{1,3}\s*(.+)', sec)
        name = header_match.group(1) if header_match else 'intro'
        chunks.append({'file': path, 'name': name, 'kind': 'doc_section',
                        'start': None, 'end': None, 'text': sec[:1000]})
    return chunks

def run(repo_path, repo_label, queries):
    print(f"\n{'='*70}\nREPO: {repo_label}\n{'='*70}")
    buckets = walk_repo(repo_path)
    print(f"[Repository Analyzer] source={len(buckets['source'])}  "
          f"doc={len(buckets['doc'])}  config={len(buckets['config'])}  "
          f"asset(ignored)={len(buckets['asset'])}  other={len(buckets['other'])}")

    all_chunks = []
    for f in buckets['source']:
        all_chunks.extend(parse_source(f))
    for f in buckets['doc']:
        all_chunks.extend(parse_doc(f))

    print(f"[Code/Text Chunking] total chunks extracted = {len(all_chunks)}")
    by_kind = {}
    for c in all_chunks:
        by_kind[c['kind']] = by_kind.get(c['kind'], 0) + 1
    print(f"   breakdown by kind: {by_kind}")
    print(f"[Metadata] config files found: {[os.path.relpath(f, repo_path) for f in buckets['config']][:8]}"
          f"{' ...' if len(buckets['config']) > 8 else ''}")

    if not all_chunks:
        print("[FAISS/RAG] no chunks to index, skipping retrieval demo.")
        return

    texts = [c['text'] for c in all_chunks]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=4000)
    matrix = vectorizer.fit_transform(texts)

    print(f"[Embedding Generation -> Vector Index] indexed {matrix.shape[0]} chunks, "
          f"{matrix.shape[1]} features (TF-IDF stand-in for embeddings/FAISS \u2014 "
          f"no model download available in this sandbox)")

    for q in queries:
        qvec = vectorizer.transform([q])
        sims = cosine_similarity(qvec, matrix).flatten()
        top_idx = sims.argsort()[::-1][:2]
        print(f"\n[RAG Retrieval] Query: \"{q}\"")
        for idx in top_idx:
            c = all_chunks[idx]
            rel_path = os.path.relpath(c['file'], repo_path)
            loc = f"lines {c['start']}-{c['end']}" if c['start'] else ""
            print(f"   -> score={sims[idx]:.3f}  {rel_path}  ::  {c['name']} ({c['kind']}) {loc}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Step 1: Repository Checker + Analyzer + Parser + Chunker + Retrieval demo")
    ap.add_argument("repo_path", help="Path to a locally cloned repository (run `git clone <url> repo_folder` first)")
    ap.add_argument("repo_label", help="A short display name for this repo, e.g. Food_ordering_WebAPP")
    ap.add_argument("queries", nargs="+", help="One or more natural-language questions to test retrieval with")
    args = ap.parse_args()
    run(args.repo_path, args.repo_label, args.queries)
