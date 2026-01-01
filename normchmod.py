#!/data/data/com.termux/files/usr/bin/python
import os
import stat


def normalize_permissions(home_directory):
    # Set the desired permissions
    dir_permissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH  # 775
    file_permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH  # 664

    # Walk through the home directory
    for root, dirs, files in os.walk(home_directory):
        # Normalize directory permissions
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.chmod(dir_path, dir_permissions)
            print(
                f'Set permissions for directory: {dir_path} to {oct(dir_permissions)}'
            )

        # Normalize file permissions
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, file_permissions)
            print(
                f'Set permissions for file: {file_path} to {oct(file_permissions)}'
            )


if __name__ == "__main__":
    home_dir = os.environ['HOME']  # Get the home directory
    normalize_permissions(home_dir)
