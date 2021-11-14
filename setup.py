import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="randfunc",
    version="0.0.3",
    author="Diwan Mohamed Faheer",
    author_email="diwanmohamedfaheer@gmail.com",
    description="A package full of random functions...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cu3t0m/randfunc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["art==5.3", "instant-api-client==0.1.2"],    
)