{
'name': "Library Books",
'summary': "Organiza tus libros",
'author': "Luis Millan",
'depends': ['base'],
'category': 'Library',
#'data': ['security/groups.xml', 'views/library_book.xml', 'views/prueba_view.xml', 'security/ir.model.access.csv'],
'data': ['security/library_security.xml', 'security/groups.xml', 'views/library_book.xml', 'views/prueba_view.xml', 'security/ir.model.access.csv'],
'application': True,
}
