# Clear Browser Cache - Important!

The browser may be caching the old model.json file. Please clear the cache:

## Chrome/Edge:
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh the page (`Ctrl + F5` or `Shift + F5`)

## Or Hard Refresh:
- Windows: `Ctrl + F5` or `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

## Or Clear Cache for This Site:
1. Press `F12` (Developer Tools)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## Verify New Model is Loading:
1. Open Developer Tools (F12)
2. Go to Network tab
3. Refresh page
4. Look for `model.json` request
5. Check the "Size" column - should show the new file size
6. Click on `model.json` to see its contents

If you still see the old model, the cache isn't cleared properly.

