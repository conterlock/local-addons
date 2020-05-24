{
    'name': "Product_prices_limit",
    'description': "Modifica la visibilidad de precios y tarifas de productos",
    'author': "Luis Millan",
    'depends': ['sale'],
    'data': ['security/product_prices_security.xml', 'views/product_prices_view.xml'],
    'application': True,
}
