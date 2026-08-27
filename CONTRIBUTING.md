# Contributing

1. **Теги неподвижны.** `git tag -f` запрещён; багфикс = новый тег.
2. **CHANGELOG на каждый тег.** Запись обязательна перед релизом.
3. **Deprecation.** `warnings.warn(DeprecationWarning, stacklevel=2)` в точке использования; старое поведение живёт ≥1 минорный тег; warning называет замену.
