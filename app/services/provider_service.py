from ..repositories.provider_repository import ProviderRepository
from ..utils.errors import AppError


class ProviderService:
    @staticmethod
    def list_all():
        return ProviderRepository.get_all()

    @staticmethod
    def get_by_id(provider_id):
        provider = ProviderRepository.get_by_id(provider_id)
        if not provider:
            raise AppError('Proveedor no encontrado', 404)
        return provider

    @staticmethod
    def create(validated_data):
        return ProviderRepository.create(validated_data)

    @staticmethod
    def update(provider_id, validated_data):
        provider = ProviderRepository.get_by_id(provider_id)
        if not provider:
            raise AppError('Proveedor no encontrado', 404)

        old_data = {
            'name':        provider.name,
            'contact':     provider.contact,
            'phone':       provider.phone,
            'description': provider.description,
        }

        updated = ProviderRepository.update(provider, validated_data)
        return updated, old_data

    @staticmethod
    def delete(provider_id):
        provider = ProviderRepository.get_by_id(provider_id)
        if not provider:
            raise AppError('Proveedor no encontrado', 404)

        deleted_name = provider.name
        ProviderRepository.delete(provider)
        return deleted_name