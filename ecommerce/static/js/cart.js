

var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
    var val = document.getElementById("cart-total").textContent
    val ++;
    console.log('new cart', val)
    document.getElementById("cart-total").innerHTML = val
    var productId = this.dataset.product
    var action = this.dataset.action
    console.log('productId:', productId, 'action :', action)

    console.log('USER :', user)

    if (user === 'AnonymousUser'){
        
        // alert('Please login to continue');
        // window.location.href = "/login"
        addCookieItem(productId, action)
    }else{
        updateUserOrder(productId, action)
    }

    })
}

function addCookieItem(productId, action){
    console.log('User not logged in...')
    if (action == 'add'){
		if (cart[productId] == undefined){
		cart[productId] = {'quantity':1}

		}else{
			cart[productId]['quantity'] += 1
		}
	}

	if (action == 'remove'){
		cart[productId]['quantity'] -= 1

		if (cart[productId]['quantity'] <= 0){
			console.log('Item should be deleted')
			delete cart[productId];
		}
    }
    console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
    // location.reload()
    
}

function updateUserOrder(productId, action){

    console.log('User logged in, sending data...')

    var url = '/update_item/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,

        },
        body:JSON.stringify({'productId':productId, 'action':action})

    })

    .then((response)=>{
        return response.json()
    })

    .then((data)=>{
        console.log('Data:',data)
        // location.reload()
    })
}