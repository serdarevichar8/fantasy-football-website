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

document.addEventListener('DOMContentLoaded', () => {
  const filterTablePairs = [
    ['lineup-filter', 'lineup-table'],
    ['draft-filter', 'league-draft-table'],
    ['draft-filter', 'league-draft-table']
    // Add more pairs as needed
  ];

  filterTablePairs.forEach(([filterID, tableID]) => {
    const filter = document.getElementById(filterID);
    const table = document.getElementById(tableID);

    if (filter && table) {
      tableFilter(filterID, tableID);
    }
  });
});