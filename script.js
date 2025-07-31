function draftTableFilter() {
    const dropdownValue = document.getElementById('draft-filter').value
    const rows = document.querySelectorAll('.content-container #league-draft-table tbody tr')

    rows.forEach(row => {
        const id = row.id
        const value = id.split('-')[1]
        if (value === dropdownValue || dropdownValue === 'all') {
            row.style.display = ''
        } else {
            row.style.display = 'none'
        }
    });
}