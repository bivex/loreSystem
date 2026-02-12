⏺ Да, UTM поддерживает shared folders! Есть несколько способов:                        
                                                                                       
  Методы shared folders в UTM                   
                                                                                       
  1. Directory Sharing (самый простой)                                                 
                                                                                       
  При создании/редактировании VM:                                                      
                                                                                       
  Settings → Drives → Directory Share                                                  

  Как настроить:
  - В настройках VM → Drives → Add → Directory Share
  - Выбрать папку на macOS для шеринга
  - Указать точку монтирования внутри Linux (обычно /mnt/shared)

  В Debian (гость) будет доступно как:
  /mnt/shared

  2. SPICE WebDAV (рекомендуется)

  Более надёжный метод с автоматическим монтированием.

  Настройка в UTM:
  Settings → Drives → Add → Directory Share
  → Type: SPICE WebDAV
  → Выбрать папку на macOS

  Монтирование в Debian:
  # Установка пакета
  sudo apt install spice-webdavd

  # Монтирование (обычно автоматически)
  # Или вручную:
  sudo mount -t davfs http://localhost:9843 /mnt/shared

  3. SSH/SFTP (для linux guest)

  # На Debian
  sudo apt install openssh-server
  sudo systemctl enable ssh
  sudo systemctl start ssh

  # С macOS (хост)
  sshfs user@vm-ip:/remote/path /local/mount

  4. 9P VirtFS (для Linux VM)

  В UTM:
  Settings → Drives → Add → Directory Share
  → Type: 9P

  В Debian:
  # Добавить в /etc/fstab:
  tag   /mnt/shared   9p   trans=virtio,version=9p2000.L   0   0

  # Смонтировать:
  sudo mkdir -p /mnt/shared
  sudo mount /mnt/shared

  Рекомендация для Debian

  Используйте SPICE WebDAV - это самый стабильный метод:
  Метод: SPICE WebDAV
  Преимущества: ✓ Стабильный✓ Авто-монтирование✓ Хорошая производительность
  Недостатки: Требует пакет в Debian
  ────────────────────────────────────────
  Метод: 9P
  Преимущества: ✓ Быстрый✓ Нативный для Linux
  Недостатки: Иногда нестабилен
  ────────────────────────────────────────
  Метод: SSH/SFTP
  Преимущества: ✓ Простой✓ Надёжный
  Недостатки: МедленнееТребует настройку
  Быстрая настройка для Debian ISO

  1. В UTM:
    - Settings → Drives → Add → Directory Share
    - Type: SPICE WebDAV
    - Path: выбрать папку на macOS
  2. В Debian после установки:
  sudo apt update
  sudo apt install spice-vdagent spice-webdavd
  sudo systemctl enable spice-webdavd
  sudo systemctl start spice-webdavd

  # Проверка - папка должна появиться в:
  ls /media/spice/

  3. Готово! Файлы будут доступны через файловый менеджер Debian или в /media/spice/...
