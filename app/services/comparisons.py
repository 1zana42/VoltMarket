from typing import List, Dict
from app.config import settings
from app.exceptions.base import ObjectNotFoundError
from app.schemes.comparisons import ComparisonGet, ComparisonItemGet
from app.services.base import BaseService


class ComparisonsService(BaseService):
    
    async def get_user_comparisons(self, user_id: int) -> List[ComparisonGet]:
        """Получение списка сравнений пользователя"""
        comparisons = await self.db.comparisons.get_user_comparisons(user_id)
        return comparisons
    
    async def create_comparison(self, user_id: int, comparison_data) -> int:
        """Создание нового сравнения"""
        comparison = await self.db.comparisons.add_comparison(
            user_id=user_id,
            name=comparison_data.name
        )
        await self.db.commit()
        return comparison.id
    
    async def add_item_to_comparison(self, user_id: int, comparison_id: int, item_id: int):
        """Добавление товара в сравнение"""
        # Проверяем существование сравнения
        comparison = await self.db.comparisons.get_one_or_none(
            id=comparison_id, 
            user_id=user_id
        )
        
        if not comparison:
            raise ObjectNotFoundError("Сравнение не найдено")
        
        # Проверяем существование товара
        item = await self.db.items.get_one_or_none(id=item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
        
        # Проверяем лимит товаров в сравнении
        item_count = await self.db.comparison_items.count_by_comparison(comparison_id)
        if item_count >= settings.MAX_COMPARISON_ITEMS:
            raise ValueError(f"Максимальное количество товаров для сравнения: {settings.MAX_COMPARISON_ITEMS}")
        
        # Проверяем, не добавлен ли уже этот товар
        existing = await self.db.comparison_items.get_one_or_none(
            comparison_id=comparison_id,
            item_id=item_id
        )
        
        if existing:
            raise ValueError("Товар уже добавлен в сравнение")
        
        # Добавляем товар
        await self.db.comparison_items.add_item(comparison_id, item_id)
        await self.db.commit()
    
    async def remove_item_from_comparison(self, user_id: int, comparison_id: int, item_id: int):
        """Удаление товара из сравнения"""
        # Проверяем существование сравнения
        comparison = await self.db.comparisons.get_one_or_none(
            id=comparison_id, 
            user_id=user_id
        )
        
        if not comparison:
            raise ObjectNotFoundError("Сравнение не найдено")
        
        # Удаляем товар
        await self.db.comparison_items.delete(
            comparison_id=comparison_id,
            item_id=item_id
        )
        await self.db.commit()
    
    async def get_comparison_details(self, user_id: int, comparison_id: int) -> Dict:
        """Получение детального сравнения с характеристиками"""
        # Проверяем существование сравнения
        comparison = await self.db.comparisons.get_one_or_none_with_items(
            id=comparison_id, 
            user_id=user_id
        )
        
        if not comparison:
            raise ObjectNotFoundError("Сравнение не найдено")
        
        # Получаем характеристики всех товаров
        items_with_specs = []
        all_spec_types = set()
        
        for comp_item in comparison.items:
            item = await self.db.items.get_with_specifications(comp_item.item_id)
            
            if item:
                # Формируем словарь характеристик
                specs_dict = {
                    spec.specification_type.name: {
                        "value": spec.value,
                        "unit": spec.specification_type.unit
                    }
                    for spec in item.specifications
                }
                
                # Собираем все типы характеристик
                all_spec_types.update(specs_dict.keys())
                
                items_with_specs.append({
                    "id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "image_url": item.main_image_url,
                    "specifications": specs_dict
                })
        
        # Формируем таблицу сравнения
        comparison_table = []
        
        for spec_type in sorted(all_spec_types):
            row = {"characteristic": spec_type}
            
            for item in items_with_specs:
                if spec_type in item["specifications"]:
                    spec = item["specifications"][spec_type]
                    row[f"item_{item['id']}"] = {
                        "value": spec["value"],
                        "unit": spec.get("unit")
                    }
                else:
                    row[f"item_{item['id']}"] = {"value": "-", "unit": None}
            
            comparison_table.append(row)
        
        return {
            "comparison": ComparisonGet.model_validate(comparison, from_attributes=True),
            "items": items_with_specs,
            "comparison_table": comparison_table
        }