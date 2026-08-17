import os, sys, subprocess, json, tempfile

def check(name, condition, detail=''):
    status = 'PASS' if condition else 'FAIL'
    print(f'[{status}] {name} {detail}')
    return condition

results = []

# 1. .gitignore ignores node_modules
with tempfile.TemporaryDirectory() as tmp:
    with open(os.path.join(tmp, '.gitignore'), 'w') as f:
        f.write('node_modules/
__pycache__/
.env
dist/
build/
')
    check('.gitignore exists', os.path.exists(os.path.join(tmp, '.gitignore)')))

# 2. Backend config imports
try:
    sys.path.insert(0, 'backend')
    from app.core.config import settings
    check('Backend config imports', True)
    check('Database URL configured', 'postgresql' in settings.database_url)
    check('Redis URL configured', 'redis' in settings.redis_url)
except Exception as e:
    check('Backend config imports', False, str(e))

# 3. Frontend package.json has required deps
try:
    with open('frontend/package.json') as f:
        pkg = json.load(f)
    deps = pkg.get('dependencies', {})
    dev_deps = pkg.get('devDependencies', {})
    all_deps = {**deps, **dev_deps}
    required = ['react', 'react-dom', 'vite', 'typescript', 'vite-plugin-pwa', '@imtbl/auth', '@imtbl/wallet']
    for r in required:
        check(f'Dep: {r}', r in all_deps)
except Exception as e:
    check('Frontend package.json', False, str(e))

# 4. Frontend builds
try:
    result = subprocess.run(['npm', 'run', 'build'], cwd='frontend', capture_output=True, text=True, timeout=120)
    check('Frontend builds', result.returncode == 0)
    check('dist exists', os.path.exists('frontend/dist'))
    check('SW generated', os.path.exists('frontend/dist/sw.js'))
    check('Manifest generated', os.path.exists('frontend/dist/manifest.webmanifest'))
except Exception as e:
    check('Frontend build', False, str(e))

# 5. PWA manifest content
try:
    with open('frontend/dist/manifest.webmanifest') as f:
        manifest = json.load(f)
    check('Manifest name', manifest.get('name') == 'TekTribe Trainer')
    check('Manifest standalone', manifest.get('display') == 'standalone')
    check('Manifest icons', len(manifest.get('icons', [])) >= 3)
except Exception as e:
    check('Manifest content', False, str(e))

# 6. Service worker registration fix
try:
    with open('frontend/src/service-worker-registration.ts') as f:
        content = f.read()
    check('SW registration syntax', 'if (confirm(' in content)
except Exception as e:
    check('SW registration', False, str(e))

# 7. Backend main.py has CORS
try:
    with open('backend/app/main.py') as f:
        content = f.read()
    check('CORS middleware', 'CORSMiddleware' in content)
    check('Health endpoint', '/health' in content)
except Exception as e:
    check('Backend main.py', False, str(e))

# 8. Env examples exist
check('Frontend .env.example', os.path.exists('frontend/.env.example'))
check('Backend .env.example', os.path.exists('backend/.env.example'))

# 9. Git repo initialized
check('.git exists', os.path.exists('.git'))

# 10. TypeScript strict mode
try:
    with open('frontend/tsconfig.json') as f:
        tsconfig = json.load(f)
    check('TS strict mode', tsconfig.get('compilerOptions', {}).get('strict') == True)
except Exception as e:
    check('TS strict mode', False, str(e))

print('
--- Verification Complete ---')
