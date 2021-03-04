function getCookie(name){
    var cookieArr = document.cookie.split(";");

    for(var i = 0; i < cookieArr.length; i++){
        var cookiePair = cookieArr[i].split("=");

        if(name == cookiePair[0].trim()){
            return decodeURIComponent(cookiePair[1]);
        }
    }

    return null;
}

var pi = getCookie('pi')

if (pi == undefined){
    pi = 0;
    document.cookie = 'pi=' + pi + ";domain=;path=/"
}

function setCookiePi(id) {
    document.cookie = 'pi=' + id + ";domain=;path=/"
}

var cart = JSON.parse(getCookie('cart'));

if (cart == undefined){
    cart = {}
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
}

function addCookieItem(id, stock){

    stock = parseInt(stock);

    if(document.querySelector('.num' + id)) {
        let num  = document.querySelector('.num' + id);
        var c = Math.round(num.value);
        num.value = c;
    }
    else {
        var c = 1;
    }

    if(cart[id] == undefined){
        cart[id] = {'cantidad':c}
    }else{
        cart[id]['cantidad'] += c
    }

    if(cart[id]['cantidad'] > stock) {
        alert(`Stock: ${stock}`);
        cart[id]['cantidad'] = stock;
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload();
}

function updateCookieItem(id, stock) {

    stock = parseInt(stock);

    var num  = document.querySelector('.num' + id);
    var c = Math.round(num.value);
    num.value = c;
    
    if(cart[id] != undefined) {
        cart[id] = {'cantidad': c}
    }

    if(cart[id]['cantidad'] > stock) {
        alert(`Stock: ${stock}`);
        cart[id]['cantidad'] = stock;
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload();
}

function removeCookieItem(id) {
    if(cart[id] != undefined) {
        delete cart[id]
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload();
}

console.log('Cart:',cart)
