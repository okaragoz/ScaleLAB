# ScaleLAB

Flow-law viscosity of a planetary lithosphere, scaled to an analogue experiment.
One static page, no build step, no server.

## Put it on GitHub Pages

1. Create a new public repository on GitHub, for example `scalelab`.
2. Upload everything in this folder, including the hidden files `.pages.yml`, `.nojekyll` and the `.github` folder.
3. In the repository: Settings, then Pages, then "Deploy from a branch", branch `main`, folder `/ (root)`.
4. After a minute the app is at `https://<your-user>.github.io/scalelab/`.

## Edit the databases without code

The flow laws and lab materials are two files: `data/flowlaws.json` and `data/materials.json`.

1. Go to https://app.pagescms.org and sign in with GitHub.
2. Give Pages CMS access to this repository and open it.
3. "Flow laws" and "Lab materials" each open a form. Add or change an entry and save.
4. Each save is a commit. GitHub Pages republishes and the app shows the new entry.

`.pages.yml` defines those forms. It was written from the Pages CMS documentation and has not been run against the service: if a form does not appear, that file is the place to look.

Units for flow laws: A in MPa^-n um^p s^-1, E in kJ/mol, V in cm3/mol.
Status values: `checked` (matched to the source), `partial` (n and Q matched, A not), `memory` (unverified).

In the app, "Add flow law" saves a private law in your browser. "Copy library JSON" gives the full
`data/flowlaws.json` including private laws, ready to paste into the repository.

## Checks

`node tests/validate.js` checks every database entry and runs the physics tests on it.
The same check runs on every push (Actions tab). A red cross means a CMS edit broke an entry.

After changing the built-in defaults inside `index.html`, run `node tests/validate.js --export` to rewrite the data files from them.

## Offline

`index.html` works by double-click without the data folder: it then uses the laws and materials embedded in the file.
