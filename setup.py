from setuptools import setup, find_packages

# Читаем содержимое README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="yt2md",
    version="0.0.4",
    description="Convert YouTube videos to Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael",
    author_email="x30827pos@gmail.com",
    url="https://github.com/xpos587/yt2md",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["aiohttp", "orjson", "aiohttp_socks"],
    entry_points={
        "console_scripts": [
            "yt2md=yt2md:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.12",
)
