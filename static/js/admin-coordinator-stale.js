document.addEventListener("DOMContentLoaded", () => {
    const markers = document.querySelectorAll('span[data-stale="1"]');
    markers.forEach((marker) => {
        const row = marker.closest("tr");
        if (row) {
            row.classList.add("coordinator-stale-row");
        }
    });
});
