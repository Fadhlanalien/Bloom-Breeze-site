
function changeimage(thumbnail) {           //  thumbnail = the element selected by using 'this' consider as a value of thumbnail?

    const mainImage = document.getElementById("main-product-image");    // mainImage = entire image tag which has the id as 'main-product-image'
                                                                        // example: mainImage = <img id="main-product-image" src="/static/images/white.jpg" alt="T-shirt">

    mainImage.src = thumbnail.src;          //  mainImage.src is property (src) of mainImage (properties of mainImage are id, src, alt, and style )
                                            //  the value of mainImage.src and thumbnail.src are something like 'static/images/product_name.jpg'.

}