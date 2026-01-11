document.addEventListener("DOMContentLoaded", () => {
    const markers = document.querySelectorAll(".active-alerts-count");
    markers.forEach((marker) => {
        const count = Number(marker.dataset.count || 0);
        if (count > 0) {
            const row = marker.closest("tr");
            if (row) {
                row.classList.add("has-active-alerts");
            }
        }
    });
});
