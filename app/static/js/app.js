document.addEventListener("DOMContentLoaded", function () {
    const itemsContainer = document.getElementById("itemsContainer");
    const addItemBtn = document.getElementById("addItemBtn");
    const removeItemBtn = document.getElementById("removeItemBtn");
    const previewBtn = document.getElementById("previewBtn");
    const clearBtn = document.getElementById("clearBtn");
    const orderForm = document.getElementById("orderForm");
    const jsonPreview = document.getElementById("jsonPreview");
    const grandTotal = document.getElementById("grandTotal");
    const searchInput = document.getElementById("searchInput");
    const ordersTable = document.getElementById("ordersTable");
    const toast = document.getElementById("toast");
    const formMode = document.getElementById("form_mode");
    const submitBtn = document.getElementById("submitBtn");
    const orderIdInput = document.getElementById("order_id");
    const mainPriceInput = document.getElementById("main_price");

    function showToast(message) {
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 1800);
    }

    function createRow(name = "", price = "") {
        const row = document.createElement("div");
        row.className = "item-row";
        row.innerHTML = `
            <input type="text" name="item_name[]" placeholder="Item Name" value="${name}">
            <input type="number" step="0.01" min="0" name="item_price[]" placeholder="Price" value="${price}">
        `;
        return row;
    }

    function getRows() {
        return itemsContainer.querySelectorAll(".item-row");
    }

    function updateTotal() {
        let total = 0;

        const mainPrice = parseFloat(mainPriceInput.value);
        if (!isNaN(mainPrice)) {
            total += mainPrice;
        }

        document.querySelectorAll('input[name="item_price[]"]').forEach(input => {
            const value = parseFloat(input.value);
            if (!isNaN(value)) {
                total += value;
            }
        });

        grandTotal.textContent = `$${total.toFixed(2)}`;
        return total;
    }

    function collectItems() {
        const names = document.querySelectorAll('input[name="item_name[]"]');
        const prices = document.querySelectorAll('input[name="item_price[]"]');
        const items = [];

        for (let i = 0; i < names.length; i++) {
            const name = names[i].value.trim();
            const price = prices[i].value.trim();

            if (name || price) {
                items.push({
                    item_name: name,
                    price: price ? parseFloat(price) : 0
                });
            }
        }

        return items;
    }

    function updatePreview() {
        const data = {
            customer_name: document.getElementById("customer_name").value.trim(),
            order_id: document.getElementById("order_id").value.trim(),
            status: document.getElementById("status").value,
            category: document.getElementById("category").value,
            main_price: parseFloat(mainPriceInput.value) || 0,
            details: document.getElementById("details").value.trim(),
            total_amount: parseFloat(updateTotal().toFixed(2)),
            items: collectItems()
        };

        jsonPreview.textContent = JSON.stringify(data, null, 4);
    }

    function filterOrders() {
        const q = searchInput.value.toLowerCase();
        ordersTable.querySelectorAll("tbody tr").forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? "" : "none";
        });
    }

    addItemBtn.addEventListener("click", function () {
        itemsContainer.appendChild(createRow());
        updatePreview();
        showToast("Item added");
    });

    removeItemBtn.addEventListener("click", function () {
        const rows = getRows();
        if (rows.length > 1) {
            rows[rows.length - 1].remove();
            updatePreview();
            showToast("Item removed");
        } else {
            showToast("At least one item row is required");
        }
    });

    previewBtn.addEventListener("click", function () {
        updatePreview();
        showToast("Preview updated");
    });

    clearBtn.addEventListener("click", function () {
        setTimeout(() => {
            getRows().forEach((row, index) => {
                if (index > 0) row.remove();
            });

            const firstRow = getRows()[0];
            if (firstRow) {
                firstRow.querySelector('input[name="item_name[]"]').value = "";
                firstRow.querySelector('input[name="item_price[]"]').value = "";
            }

            formMode.value = "create";
            submitBtn.textContent = "Save Order";
            orderIdInput.readOnly = false;
            document.getElementById("category").value = "";
            jsonPreview.textContent = "No preview yet...";
            updateTotal();
        }, 50);
    });

    orderForm.addEventListener("input", updatePreview);
    searchInput.addEventListener("input", filterOrders);

    window.editOrder = function (order) {
        document.getElementById("customer_name").value = order.customer_name || "";
        document.getElementById("order_id").value = order.order_id || "";
        document.getElementById("status").value = order.status || "Pending";
        document.getElementById("category").value = order.category || "";
        document.getElementById("details").value = order.details || "";
        mainPriceInput.value = order.main_price ?? "";

        itemsContainer.innerHTML = "";

        if (order.items && order.items.length > 0) {
            order.items.forEach(item => {
                itemsContainer.appendChild(createRow(item.item_name || "", item.price || ""));
            });
        } else {
            itemsContainer.appendChild(createRow());
        }

        formMode.value = "update";
        submitBtn.textContent = "Update Order";
        orderIdInput.readOnly = true;

        updatePreview();
        showToast("Edit mode enabled");
    };

    window.deleteOrder = function (orderId) {
        if (!confirm(`Delete ${orderId}?`)) return;

        fetch(`/delete_order/${orderId}`, {
            method: "POST"
        })
        .then(response => {
            if (response.ok) {
                showToast("Order deleted");
                setTimeout(() => {
                    location.reload();
                }, 500);
            } else {
                alert("Delete failed");
            }
        })
        .catch(() => {
            alert("Delete failed");
        });
    };

    updatePreview();
});