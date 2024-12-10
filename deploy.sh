rm -r dist/
cd frontend
npm install
npm run build
cp -r dist ../backend
cd ..
git add ./backend/dist
git commit -m "Deploy"
git push heroku main
