from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="yt2md",
    version="1.0.0",
    description="A tool to convert YouTube videos to Markdown format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael",
    author_email="x30827pos@gmail.com",
    url="https://github.com/xpos587/yt2md",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["yt2md"],
    install_requires=["aiohttp", "aiohttp_socks"],
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)
