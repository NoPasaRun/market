// Кнопка добавление выбранного количества товаров случайного продавца в корзину на странице просмотра товара
window.onload = function() {
    const buyBtn =  document.querySelector("#BuyBtn");
    if (buyBtn) {
            buyBtn.onclick = function(){
            const amount = document.querySelector("#AmountInput").value;
            const productID =  location.pathname.split('/')[2];
            const url = `/add_to_cart/?product_id=${productID}&amount=${amount}`;

            var request = new XMLHttpRequest();
            request.open("GET", url);
            request.send();
            request.onload = function() {
                 location.reload();
            };
        };
    };
};