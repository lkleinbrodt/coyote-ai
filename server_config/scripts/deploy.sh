rm -r dist/
cd frontend
npm install
if npm run build; then
    cp -r dist ../
    cd ..
    git add ./dist
    git commit -m "Deploy"
    git push heroku main
else
    echo "Build failed - deployment aborted"
    exit 1
fi
