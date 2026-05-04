const fs = require('fs');

async function loadData() {
    const res = await fetch('http://localhost:1337/api/modules?populate=*');
    const modules = await res.json();
    const dataStr = JSON.stringify(modules, null, 2);
    const fileContent = `const modules = ${dataStr};`;

    fs.writeFile('./www/data.js', fileContent, (err) => {
        if (err) {
            console.error('Error writing file:', err);
            return;
        }

        console.log('The file has been saved!');
    });
}

loadData();