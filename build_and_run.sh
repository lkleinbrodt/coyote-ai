rm -r dist/
cd frontend
npm install
npm run build
cp -r dist ../
cd ..
gunicorn backend.app:app