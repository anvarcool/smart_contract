# В данном репозитории реализован смарт-контракт системы "электронного журнала"
Для проведения тестов с использованием hardhat нужно прописать в терминале: \
cd 'Путь к папке с репозиторием' \
npx hardhat init \
npx hardhat compile \
npx hardhat test

После инициализации проекта hardhat:
npx hardhat node - чтобы создать локальный блокчейн
npx hardhat ignition deploy ./ignition/modules/Education_system.ts

потом копируем юнит тесты из backend unit tests, вставляя новые адреса и приватные ключи и радуемся жизни (надо вставить в консоль, естественно)
