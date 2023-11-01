from setuptools import setup, find_packages

setup(
    name="certbot-dns-lexicon",
    version="1.0.27",
    author="Maciej Szczurek",
    python_requires=">=3.10",
    packages=find_packages(exclude=["lexicon", "lexicon.*"]),
    install_requires=[
        "certbot==2.7.4",
        "PyYAML==6.0",
        "dns-lexicon==3.16.1",
        "beautifulsoup4==4.12.2",
        "requests==2.31.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-lexicon = certbot_dns_lexicon._internal.dns_lexicon:Authenticator",
        ],
    },
)
