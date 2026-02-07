"""
Script de migración para agregar soporte de múltiples imágenes por producto.

Pasos:
1. Crea tabla product_images
2. Migra imágenes existentes de product.image_path a product_images
3. Marca imágenes migradas como principales

Ejecutar: python migrate_product_images.py
"""

import sys
import os

# Agregar path para imports
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.database import db
from app.models.product import Product

def migrate_product_images():
    """Migrar imágenes existentes a la nueva tabla"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de imágenes de productos...")
        
        # 1. Crear tabla product_images si no existe
        print("📊 Creando tabla product_images...")
        try:
            db.create_all()
            print("✅ Tabla product_images creada/verificada")
        except Exception as e:
            print(f"❌ Error creando tabla: {e}")
            return
        
        # Importar ProductImage después de crear la tabla
        try:
            from app.models.product_image import ProductImage
        except ImportError as e:
            print(f"❌ Error importando ProductImage: {e}")
            print("   Asegúrate de que product_image.py está en app/models/")
            return
        
        # 2. Migrar imágenes existentes
        try:
            products_with_images = Product.query.filter(Product.image_path.isnot(None)).all()
        except Exception as e:
            print(f"❌ Error consultando productos: {e}")
            return
        
        if not products_with_images:
            print("ℹ️  No hay productos con imágenes para migrar")
            return
        
        print(f"📦 Encontrados {len(products_with_images)} productos con imágenes")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for product in products_with_images:
            try:
                # Verificar si ya tiene imágenes en la nueva tabla
                existing_images = ProductImage.query.filter_by(product_id=product.id).count()
                
                if existing_images > 0:
                    print(f"⏭️  Producto {product.id} ({product.name}) ya tiene imágenes migradas, saltando...")
                    skipped_count += 1
                    continue
                
                # Crear ProductImage desde image_path legacy
                product_image = ProductImage(
                    product_id=product.id,
                    image_path=product.image_path,
                    is_primary=True,  # Marcar como principal
                    display_order=0
                )
                
                db.session.add(product_image)
                migrated_count += 1
                print(f"✅ Migrado: Producto {product.id} ({product.name})")
                
            except Exception as e:
                print(f"❌ Error migrando producto {product.id}: {e}")
                error_count += 1
                continue
        
        # Commit de todas las migraciones
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Migración completada!")
            print(f"📊 Productos migrados: {migrated_count}")
            print(f"⏭️  Productos saltados (ya migrados): {skipped_count}")
            if error_count > 0:
                print(f"❌ Errores: {error_count}")
            print(f"{'='*60}")
            print("\n⚠️  NOTA: El campo 'image_path' en la tabla 'products' se mantiene")
            print("   por compatibilidad pero ya NO se usa. Usar 'images' en su lugar.")
        except Exception as e:
            print(f"\n❌ Error al hacer commit: {e}")
            db.session.rollback()

if __name__ == '__main__':
    try:
        migrate_product_images()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()