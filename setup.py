from setuptools import setup, find_packages

exec(open("exceptiongroup/_version.py", encoding="utf-8").read())

LONG_DESC = open("README.rst", encoding="utf-8").read()

setup(
    name="exceptiongroup",
    version=__version__,
    description="A way to represent multiple things going wrong at the same time, in Python",
    url="https://github.com/python-trio/exceptiongroup",
    long_description=LONG_DESC,
    author="Nathaniel J. Smith",
    author_email="njs@pobox.com",
    license="MIT -or- Apache License 2.0",
    packages=find_packages(),
    install_requires=["trio"],
    keywords=["async", "exceptions", "error handling"],
    python_requires=">=3.5",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Trio",
        "Framework :: AsyncIO",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
    ],
)
