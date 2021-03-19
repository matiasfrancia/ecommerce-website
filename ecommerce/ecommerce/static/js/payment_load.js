const load_container = document.getElementById("loading")
const payment_container = document.getElementById("payments")

console.log(payment_container)

const url = "payments-json/"

fetch(url)
.then(response => response.json())
.then(data =>  {
    payment_container.innerHTML = display(data)
    load_container.style.display = "none"
})

function display(data){
    let payments = ""
    for(payment of data){
        let products_detail = ""
        if (payment.cart_products){
            let product = ""
            for(item of payment.cart_products){
                product+= `${item.product_id} - ${item.product_title}: ${item.product_quantity} <br>`
            }
            products_detail = `<p class="list">
                                    Productos comprados: <br>
                                    ${product}
                                </p>`
        }
        payments += `<div class="payment-container">
                        <p class="id">Id pago: ${payment.payment_id}</p>
                        <p class="name">Nombre cliente: <br>${payment.payer_name}</p>
                        <p class="email">Email cliente: <br>${payment.payer_email}</p>
                        ${products_detail}
                        <p class="amount">Monto de compra: ${to_clp(payment.amount)}</p>
                        <a class="refound" href="http://localhost:8000/refound/${payment.payment_id}">Reembolsar</a>
                    </div>`
    }
    
    return payments
}

function to_clp(amount){
    return Intl.NumberFormat('es-CL', {style: 'currency', currency: 'CLP'}).format(amount)
}