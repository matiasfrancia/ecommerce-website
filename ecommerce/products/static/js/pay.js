const baseRequest = {
    apiVersion: 2,
    apiVersionMinor: 0
};

/**
 * Card networks supported by your site and your gateway
 * @see {@link https://developers.google.com/pay/api/web/reference/request-objects#CardParameters|CardParameters}
 */
const allowedCardNetworks = ["AMEX", "DISCOVER", "INTERAC", "JCB", "MASTERCARD", "VISA"];

/**
 * Card authentication methods supported by your site and your gateway
 *
 * @see {@link https://developers.google.com/pay/api/web/reference/request-objects#CardParameters|CardParameters}
 */
const allowedCardAuthMethods = ["PAN_ONLY", "CRYPTOGRAM_3DS"];

const tokenizationSpecification = {
type: 'PAYMENT_GATEWAY',
parameters: {
    'gateway': 'example',
    'gatewayMerchantId': 'exampleGatewayMerchantId'
}
};

const baseCardPaymentMethod = {
type: 'CARD',
parameters: {
    allowedAuthMethods: allowedCardAuthMethods,
    allowedCardNetworks: allowedCardNetworks
}
};

const cardPaymentMethod = Object.assign(
{},
baseCardPaymentMethod,
{
    tokenizationSpecification: tokenizationSpecification
}
);

let paymentsClient = null;

function getGoogleIsReadyToPayRequest() {
return Object.assign(
    {},
    baseRequest,
    {
        allowedPaymentMethods: [baseCardPaymentMethod]
    }
);
}

function getGooglePaymentDataRequest() {
const paymentDataRequest = Object.assign({}, baseRequest);
paymentDataRequest.allowedPaymentMethods = [cardPaymentMethod];
paymentDataRequest.transactionInfo = getGoogleTransactionInfo();
paymentDataRequest.merchantInfo = {
    // @todo a merchant ID is available for a production environment after approval by Google
    // See {@link https://developers.google.com/pay/api/web/guides/test-and-deploy/integration-checklist|Integration checklist}
    merchantId: '12345678901234567890',
    merchantName: 'Example Merchant'
};
return paymentDataRequest;
}

function getGooglePaymentsClient() {
if ( paymentsClient === null ) {
    paymentsClient = new google.payments.api.PaymentsClient({environment: 'TEST'});
}
return paymentsClient;
}

function onGooglePayLoaded() {
const paymentsClient = getGooglePaymentsClient();
paymentsClient.isReadyToPay(getGoogleIsReadyToPayRequest())
    .then(function(response) {
        if (response.result) {
            addGooglePayButton();
        }
    })
    .catch(function(err) {
        // show error in developer console for debugging
        console.error(err);
    });
}

function addGooglePayButton() {
const paymentsClient = getGooglePaymentsClient();
const button =
    paymentsClient.createButton({onClick: onGooglePaymentButtonClicked});
document.getElementById('container').appendChild(button);
}

/**
 * Provide Google Pay API with a payment amount, currency, and amount status
 *
 * @see {@link https://developers.google.com/pay/api/web/reference/request-objects#TransactionInfo|TransactionInfo}
 * @returns {object} transaction info, suitable for use as transactionInfo property of PaymentDataRequest
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


function getGoogleTransactionInfo() {

    return fetch('/cart/pay', {
        method: 'POST',
        headers: {
        'content-type': 'application/json',
        'X-CSRFToken': csrftoken,
        }
    }).then(function(res){
        return res.json();
    }).then(function(data){
        console.log(data.total);

        return {
            countryCode: 'US',
            currencyCode: 'USD',
            totalPriceStatus: 'FINAL',
            // set to cart total
            totalPrice: `${data.total}`
        };
    });
}

/**
 * Show Google Pay payment sheet when Google Pay payment button is clicked
 */
function onGooglePaymentButtonClicked() {
const paymentDataRequest = getGooglePaymentDataRequest();
paymentDataRequest.transactionInfo = getGoogleTransactionInfo();

const paymentsClient = getGooglePaymentsClient();
paymentsClient.loadPaymentData(paymentDataRequest)
    .then(function(paymentData) {
        // handle the response
        processPayment(paymentData);
    })
    .catch(function(err) {
        // show error in developer console for debugging
        console.error(err);
    });
}
/**
 * Process payment data returned by the Google Pay API
 *
 * @param {object} paymentData response from Google Pay API after user approves payment
 * @see {@link https://developers.google.com/pay/api/web/reference/response-objects#PaymentData|PaymentData object reference}
 */
function processPayment(paymentData) {
// show returned data in developer console for debugging
    console.log(paymentData);
// @todo pass payment token to your gateway to process payment
paymentToken = paymentData.paymentMethodData.tokenizationData.token;
}