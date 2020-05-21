from flask import Flask, render_template
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from server.BankAdministration import BankAdministration
from server.bo.Customer import Customer
from server.bo.Account import Account
from server.bo.Transaction import Transaction
from SecurityDecorator import secured
app = Flask(__name__)

""" CORS muss hier definiert werden und der Präfix unsere Ressourcen auch 
CORS(app, resources=r'/bank/*')
"""
"""Modell aufbauen, das die Datenstruktur beschreibt, 
auf deren Basis Clients und Server Daten austauschen. Grundlage hierfür ist das Package flask-restx."""
api = Api(app, version='1.0', title='HOLMA API',
    description='Eine rudimentäre Demo-API für Listenerstellung.')

"""Namespaces"""
Listingapp = api.namespace('app', description="Funktionen der App")

"""Unsere BOs werden hier nach und nach definiert,
 zu den methoden (api.model/api.inherit) findet man mehr auf der Flask Seite unter Response marshalling
 https://flask-restplus.readthedocs.io/en/stable/marshalling.html?highlight=nested#nested-field """

bo = api.model('BusinessObject', {
    'name': fields.String(attribute='_name', description='Name eines Objekts'),
    'id': fields.Integer(attribute='_id', description='Der Unique Identifier eines Business Object'),
    'creation_date' : fields.Integer(attribute='_creation_date',
                                     description='Erstellungsdatum des BOs, wird durch Unix Time Stamp ermittlet')
})

"""mit attribute='' wird gerenamed"""
group = api.inherit('Group', bo, {
    'owner_id': fields.Integer(attribute='_owner', description='Unique Id des Kontoinhabers'),
    'members': fields.Array(attribute='_members', description='Eine liste aller Gruppenmitglieder'),
    'articles' : fields.Array(attribute='_articles',
                                     description='Liste aller Artikeln'),
    'shoppingslists' : fields.Array(attribute='_shoppinglist',
                                     description='Liste aller listen der Gruppe'),
    'standardarticles' : fields.Array(attribute='_standardarticles',
                                     description='Liste aller standardartikeln der Gruppe'),
})

person = api.inherit('Person', bo, {
    'email': fields.String(attribute='_email', description='E-Mail-Adresse eines Benutzers'),
    'groups': fields.Array(attribute='_groups',
                           description='Eine liste aller Gruppen an der die Person beteiligt ist '),
})

"""Datentyp von Gruppe?"""
shoppingList = api.inherit('ShoppingList', bo, {
    'group': fields.String(attribute='_group', description='zu welcher groupe diese Liste gehört'),
    'list_entries': fields.Array(attribute='_list_entries',
                           description='Eine liste aller list entries der List '),
})

listEntry = api.inherit('ListEntry', bo, {
    'list': fields.String(attribute='_list', description='zu welcher Liste diese Entry gehört?'),
    'article': fields.Array(attribute='_article',
                           description='zu welchem Artikle gehört dieses Entry? '),
    'amount': fields.Float(attribute='_amount',
                               description='Menge des Entries '),
    'unit': fields.Integer(attribute='_unit',
                               description='Einheit des Entries '),
    'purchasing_person': fields.String(attribute='_purchasing_person',
                               description='Wer das Artikle kaufen muss '),
    'retailer': fields.(attribute='_retailer',
                               description='Bei wem das Artikle gekauft  '),
    'checked': fields.Boolean(attribute='_checked',
                               description='wurde es bereit gekauft'),
    'standardarticle': fields.Boolean(attribute='_standardarticle',
                               description='ist es ein Standardartikle '),
})

article = api.inherit('Article', bo, {
    'group': fields.String(attribute='_group', description='zu welcher Groupe dieses Artikle gehört?'),
})
retailer = api.inherit('Retailer', bo)

@Listingapp.route('/groups')
@Listingapp.response(500,'Falls es zu einem Server-seitigem Fehler kommt.')
class GroupListOperations(Resource): """Ressource kommt von Flask x"""
    @Listingapp.marshal_list_with(group)
    @secured
    def get(self):
        """Auslesen aller Gruppen-Objekte

        Sollten keine Customer-Objekte verfügbar sein, so wird eine leere Sequenz zurückgegeben"""
        grp = AppAdministration() """wir brauchen eine AppAdministration"""
        group = grp.get_all_groups()
        return group

    @Listingapp.marshal_with(group, code=200)
    @Listingapp.expect(group) # group objekt von Client Seite wird erwatet
    @secured
    def post(self): """Groupe erstellen
        Nix verstanden"""
        return 0

@listingapp.route('/groups/<int:id>')
@listingapp.response(500,'Falls es zu einem Server-seitigen Fehler kommt.')
@listingapp('id', 'Die ID des Group-Objekts')
class GroupOperation(Resource):
    @listingapp.marshal_with(group)
    @secured
    def get(self, id):
        """Auslesen einer bestimmten Gruppe"""

        grp = AppAdministration()
        cust = grp.get_customer_by_id(id)
        return cust

    @secured
    def delete(self, id):
        """Löschen einer Gruppe durch id"""

        grp = AppAdministration()
        cust = grp.get_group_by_id(id)
        grp.delete_group(cust)
        return '', 200

    @listingapp.marshal_with(group)
    @listingapp.expect(group, validate=True)
    @secured
    def put(self, id):
        """Update eines bestimmten Customer-Objekts.
        immer noch nix verstanden"""

@listingapp.route('/groups/<string:name>')
@listingapp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@listingapp.param('name', 'Der Name der Gruppe')
class GroupsByNameOperations(Resource):
    @listingapp.marshal_with(group)
    @secured
    def get(self, name):
        """ Auslesen von Group-Objekten, die durch den Namen bestimmt werden.

        Die auszulesenden Objekte werden durch ```name``` in dem URI bestimmt.
        """
        grp = AppAdministration()
        cust = grp.get_group_by_name(name)
        return cust

@listingapp.route('/persons')
@listingapp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
class PersonsListOperations(Resource):
    @listingapp.marshal_list_with(person)
    @secured
    def get(self):
        """Auslesen aller Personen-Objekte.

        Sollten keine Personen-Objekte verfügbar sein, so wird eine leere Sequenz zurückgegeben."""
        grp = AppAdministration()
        person_list = grp.get_all_persons()
        return person_list

@listingapp.route('/persons/<int:id>')
@listingapp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@listingapp.param('id', 'Die ID des Account-Objekts')
class AccountOperations(Resource):
    @listingapp.marshal_with(person)
    @secured
    def get(self, id):
        """Auslesen eines bestimmten Person-Objekts.

        Das auszulesende Objekt wird durch die ```id``` in dem URI bestimmt.
        """
        grp = AppAdministration()
        acc = grp.get_person_by_id(id)
        return acc

    @secured
    def delete(self, id):
        """Löschen eines bestimmten Person-Objekts.

        Das zu löschende Objekt wird durch die ```id``` in dem URI bestimmt.
        """
        grp = AppAdministration()
        acc = grp.get_person_by_id(id)
        grp.delete_account(acc)
        return '', 200

    @listingapp.marshal_with(person)
    @secured
    def put(self, id):
        """Immer noch kein plan"""
        return 0

@listingapp.route('/persons/<int:id>/groups')
@listingapp.response(500, 'Falls es zu einem Server-seitigen Fehler kommt.')
@listingapp.param('id', 'Die ID des person-Objekts')
class PersonRelatedGroupOperations(Resource):
    @listingapp.marshal_with(group)
    @secured
    def get(self, id):
        """Auslesen aller Acount-Objekte bzgl. eines bestimmten Customer-Objekts.

        Das Customer-Objekt dessen Accounts wir lesen möchten, wird durch die ```id``` in dem URI bestimmt.
        """
        grp = AppAdministration()
        # Zunächst benötigen wir den durch id gegebenen Customer.
        cust = grp.get_person_by_id(id)

        # Haben wir eine brauchbare Referenz auf ein Customer-Objekt bekommen?
        if cust is not None:
            # Jetzt erst lesen wir die Konten des Customer aus.
            group_list = grp.get_groups_of_person(cust)
            return group_list
        else:
            return "Customer not found", 500

    @listingapp.marshal_with(group, code=201)
    @secured
    def post(self, id):
        """Anlegen einer Gruppe für einer gegebenen Person.

        Die neu angelegte Gruppe wird als Ergebnis zurückgegeben.

        **Hinweis:** Unter der id muss ein Customer existieren, andernfalls wird Status Code 500 ausgegeben."""
        grp = BankAdministration()
        """Stelle fest, ob es unter der id einen Customer gibt. 
        Dies ist aus Gründen der referentiellen Integrität sinnvoll!
        """
        cust = grp.get_person_by_id(id)

        if cust is not None:

            result = grp.create_group_for_person(cust)
            return result
        else:
            return "Person unknown", 500



















