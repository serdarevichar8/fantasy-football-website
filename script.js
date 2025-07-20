const params = new URLSearchParams(window.location.search);

const team = params.get('team')

console.log(team)


// const data = fetch('/fantasy-football-website/api/data.json')
//     .then(data => data.json()) 
//     .then(data => console.log(data))

async function loadData() {
    const response = await fetch('/fantasy-football-website/api/data.json')
    return await response.json()
}

async function main() {
    const data = await loadData();

    const params = new URLSearchParams(window.location.search);
    const teamParam = params.get('team')

    const df = new dfd.DataFrame(data);

    df.print()
    console.log(df)
}

main();


