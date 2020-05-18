{
    'name': "Product_prices_limit",
    'description': "Modifica la visibilidad de precios y tarifas de productos",
    'author': "Luis Millan",
    'depends': ['sale'],
    'data': ['security/product_prices_security.xml', 'security/product.pricelist.csv'],
    'application': True,
}
