rm -r dist/
cd frontend
npm install
npm run build
cp -r dist ../
cd ..
git add ./dist
git commit -m "Deploy"
git push heroku main
