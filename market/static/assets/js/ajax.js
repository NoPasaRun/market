window.addEventListener("load", function() {
    let amounts = document.querySelectorAll(".Amount")
    amounts.forEach(function(amount) {

        let update_time = 0
        let update = false
        let data = {}
        function set_update_to_true() {
            if (update_time > 0) {
                update_time -= 1
            }
        }
        setInterval(set_update_to_true, 1)

        function ajaxRequest() {
            if (update_time === 0 && update) {
                update = false
                $.ajax({
                    url: data["url"],
                    method: "GET",
                    type: "json",
                    data: {"amount": data["amount"]},
                    headers: {'X-Requested-With': 'XMLHttpRequest'},
                    success: function (data) {
                        document.querySelector(".Total-price").innerText = data["total_sum"] + '$';
                        document.querySelector(".CartBlock-price").innerText = data["total_sum"] + '$';
                        let old_total_sum = '';
                        if (data["total_sum"] != data["old_total_sum"]) {
                            old_total_sum = data["old_total_sum"] + '$';
                        }
                        document.querySelector(".Cart-price_old").innerText = old_total_sum;
                        for (id in data["prices"]) {
                            document.querySelector(`#Price-${id}`).innerText = data["prices"][id];
                        }
                        let cart_data = JSON.parse(data["cart"])
                        for (let key in cart_data) {
                            let product = document.getElementById(key)
                            $(product).attr("value", cart_data[key]["amount"])
                            if ($(product).attr("value") !== product.value) {
                                product.value = cart_data[key]["amount"]
                            }
                        }
                    }
                })
            }
        }
        setInterval(ajaxRequest, 1)

        let add_button = $(amount).find(".Amount-add")
        let remove_button = $(amount).find(".Amount-remove")
        let input = $(amount).find(".Amount-input")

        function change_values() {
            let num = input.val()-input.attr("value")
            data = {"url": "/add_to_cart/?seller_product_id=" + input.attr("id"),
            "amount": num}
            update_time = 150
            update = true
        }

        $(add_button).on("click", function() {
            setTimeout(change_values, 10)
        })

        $(remove_button).on("click", function() {
            setTimeout(change_values, 10)
        })

        $(input).on("change", function() {
            if (input.val() !== "") {
                setTimeout(change_values, 10)
            }
        })
    })
})