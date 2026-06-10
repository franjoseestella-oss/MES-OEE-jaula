import json, urllib.request, base64

auth = base64.b64encode(b'fran.jose.estella@gmail.com:admin123').decode()
req = urllib.request.Request(
    'http://localhost:3010/api/dashboards/uid/mes-log-v1',
    headers={'Authorization': f'Basic {auth}'}
)
d = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
panels = [p for p in d['dashboard']['panels'] if p.get('id') == 15]
p = panels[0]
print('min:', p['fieldConfig']['defaults']['min'])
print('max:', p['fieldConfig']['defaults']['max'])
print('thresholds:', json.dumps(p['fieldConfig']['defaults']['thresholds'], indent=2, ensure_ascii=False))
print('transformations count:', len(p.get('transformations', [])))
for i, t in enumerate(p.get('transformations', [])):
    apply_to = t['options'].get('applyTo', {}).get('options', 'N/A')
    mappings = t['options'].get('mappings', [])
    mapped_fields = [(m['fieldName'], m.get('handlerKey', '?')) for m in mappings]
    print(f'  transform {i}: {t["id"]} -> {apply_to}')
    for fn, hk in mapped_fields:
        print(f'    {fn}: {hk}')
print()
print('SQL first 300:', p['targets'][0]['rawSql'][:300])
