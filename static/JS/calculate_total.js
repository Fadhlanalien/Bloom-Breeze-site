function calculateTotal() {
    const price = parseFloat(document.getElementById("price").value) || 0;
    const quantity = parseInt(document.getElementById("quantity").value) || 0;
    const shipping = parseFloat(document.getElementById("shipping").value) || 0;
    const tax = parseFloat(document.getElementById("tax").value) || 0;

    const subtotal = price * quantity;
    const total = subtotal + shipping + tax;

    document.getElementById("sub_total").value = subtotal.toFixed(2);
    document.getElementById("total_display").value = total.toFixed(2);
    document.getElementById("total").value = total.toFixed(2);
}

document.getElementById("quantity").addEventListener("input", calculateTotal);
calculateTotal()
