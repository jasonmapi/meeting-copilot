import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'));bad=[]
for name,expected in manifest['files'].items():
 p=(root/name).resolve()
 if not p.is_relative_to(root.resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:bad.append(name)
print(json.dumps({'files':len(manifest['files']),'passed':not bad,'mismatches':bad},ensure_ascii=False))
sys.exit(bool(bad))
