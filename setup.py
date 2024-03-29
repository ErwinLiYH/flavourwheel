import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flavourwheel",
    version="2.3.0",
    author="ErwinLi",
    author_email="1779599839@qq.com",
    description="Automatical flavour wheel generation with NLP tech",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErwinLiYH/flavourwheel",
    project_urls={
        "Bug Tracker": "https://github.com/ErwinLiYH/flavourwheel/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")+["flavourwheel.template"],
    package_data={"flavourwheel.template":["template.js", "echarts.js", "index.html"]},
    python_requires=">=3.6",
)
