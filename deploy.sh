rm -r dist/
cd frontend
npm install
npm run build --mode production
cp -r dist ../
cd ..
git add ./dist
git commit -m "Deploy"
git push heroku main
