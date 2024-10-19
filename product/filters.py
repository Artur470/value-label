import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    all = django_filters.BooleanFilter(
        field_name='all',
        method='filter_all',
        label='Все товары',
        widget=django_filters.widgets.BooleanWidget()
    )
    category = django_filters.CharFilter(field_name='category__value', lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name='brand__value', lookup_expr='iexact')
    color = django_filters.CharFilter(field_name='color__value', lookup_expr='iexact')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['all', 'category', 'brand', 'color', 'price_min', 'price_max']

    def filter_all(self, queryset, name, value):
        if value:  # Если all = True, возвращаем все товары
            return Product.objects.all()  # Возвращаем все продукты без фильтров
        return queryset  # Возвращаем исходный queryset, если all не установлен
