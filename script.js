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

function findFilters() {
  const contentContainers = document.querySelectorAll('.content-container:has(select)');

  console.log(contentContainers);

  contentContainers.forEach(item => {
    const filter = item.querySelector('select')
    const filterID = filter.id
    // console.log(filterID)

    const table = item.querySelector('table')
    const tableID = table.id
    // console.log(tableID)

    tableFilter(filterID, tableID)
  })
}

document.getElementById('toggle').addEventListener('click', () => {
  document.body.classList.toggle('collapsed')
  document.getElementsByClassName('topnav')[0].classList.toggle('collapsed')
})

document.addEventListener('DOMContentLoaded', () => {
  findFilters()
});