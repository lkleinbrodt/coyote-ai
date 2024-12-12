rm -rf dist/ || true
cd frontend
npm install
npm run build
cp -r dist ../
cd ..
gunicorn app:app