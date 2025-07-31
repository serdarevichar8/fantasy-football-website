function draftTeamFilter() {
    const dropdownValue = document.getElementById('draft-team-filter').value
    const rows = document.querySelectorAll('.content-container #league-draft-table tbody tr')

    rows.forEach(row => {
        const id = row.id
        const team = id.split('-')[1]
        if (team === dropdownValue || dropdownValue === 'all') {
            row.style.display = ''
        } else {
            row.style.display = 'none'
        }
    });
}