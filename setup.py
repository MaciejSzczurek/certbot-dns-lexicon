from setuptools import setup, find_packages

setup(
    name="certbot-dns-lexicon",
    version="1.0.48",
    author="Maciej Szczurek",
    python_requires=">=3.10",
    packages=find_packages(exclude=["lexicon", "lexicon.*"]),
    install_requires=[
        "certbot==4.0.0",
        "PyYAML==6.0.2",
        "dns-lexicon==3.21.0",
        "beautifulsoup4==4.13.3",
        "requests==2.32.3",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-lexicon = certbot_dns_lexicon._internal.dns_lexicon:Authenticator",
        ],
    },
)
