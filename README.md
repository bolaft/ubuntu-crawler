# Ubuntu documentation web crawler

Downloads the online francophone Ubuntu documentation at `https://doc.ubuntu-fr.org/`.

Uses a list of pages (the `list` file) extracted from the `https://doc.ubuntu-fr.org/Accueil?do=index` summary page on October 6th, 2014. The following namespaces were ignored: `arnaud04`, `evenements`, `playground`, `projets` and `utilisateurs`.

All selected pages are downloaded in the `import` folder. Local folder hierarchy mirrors remote namespace hierarchy. Images found in web pages are also downloaded into the namespace folder. The `src` attribute of corresponding `img` tags is html files is corrected to correctly link to the locally stored image.