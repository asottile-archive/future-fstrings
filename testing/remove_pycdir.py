import os.path
import shutil


def main():
    pth = 'tests/__pycache__'
    if os.path.exists(pth):
        shutil.rmtree(pth)


if __name__ == '__main__':
    exit(main())
