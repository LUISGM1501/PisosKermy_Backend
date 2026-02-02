from ..database import db
from ..models import Provider


class ProviderRepository:
    @staticmethod
    def get_all():
        return Provider.query.order_by(Provider.name).all()

    @staticmethod
    def get_by_id(provider_id):
        return db.session.get(Provider, provider_id)

    @staticmethod
    def create(data):
        provider = Provider(
            name=data['name'],
            contact=data.get('contact'),
            phone=data.get('phone'),
            description=data.get('description'),
        )
        db.session.add(provider)
        db.session.commit()
        return provider

    @staticmethod
    def update(provider, data):
        if 'name' in data:
            provider.name = data['name']
        if 'contact' in data:
            provider.contact = data['contact']
        if 'phone' in data:
            provider.phone = data['phone']
        if 'description' in data:
            provider.description = data['description']
        db.session.commit()
        return provider

    @staticmethod
    def delete(provider):
        db.session.delete(provider)
        db.session.commit()