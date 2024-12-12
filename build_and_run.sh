rm -rf dist/ || true
cd frontend
npm install
if [[ "$1" == "--dev" ]]; then
    npm run build -- --mode development
else
    npm run build
fi
cp -r dist ../
cd ..
gunicorn app:app