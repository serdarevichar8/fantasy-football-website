function tableFilter(filterID, tableID) {
    const dropdownValue = document.getElementById(`${filterID}`).value
    const rows = document.querySelectorAll(`.content-container #${tableID} tbody tr`)

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