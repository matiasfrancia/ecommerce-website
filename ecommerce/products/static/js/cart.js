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

var cart = JSON.parse(getCookie('cart'));

if (cart == undefined){
    cart = {}
    console.log('Cart created', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
}

function addCookieItem(id){

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

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload();
}

function updateCookieItem(id) {

    var num  = document.querySelector('.num' + id);
    var c = Math.round(Number(num.value));
    console.log(c);
    num.value = c;
    console.log(c);

    if(cart[id] != undefined) {
        cart[id] = {'cantidad': c}
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

    console.log("Esta funcionando la funcion remove")
}

console.log('Cart:',cart)
