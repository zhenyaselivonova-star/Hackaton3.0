from yandex_config import yandex_config


def main():
    if not yandex_config.check_config_exists():
        print("❌ Конфигурация не найдена. Сначала запустите setup.py")
        return

    yandex_config.update_keys()
    print("\n✅ Ключи обновлены! Перезапустите приложение.")


if __name__ == "__main__":
    main()