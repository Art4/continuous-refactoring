var cart = {
    items: [],
    total: function () {
        var sum = 0;
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i].quantity == '0') {
                continue;
            }
            sum += this.items[i].price * this.items[i].quantity;
        }
        return sum;
    }
};
