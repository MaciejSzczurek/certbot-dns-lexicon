from setuptools import setup, find_packages

setup(
    name="certbot-dns-lexicon",
    version="1.0.0",
    author="Maciej Szczurek",
    python_requires=">=3.10",
    packages=find_packages(exclude=["lexicon", "lexicon.*"]),
    install_requires=[
        "certbot==2.1.0",
        "PyYAML==5.4.1",
        "dns-lexicon==3.11.7",
        "beautifulsoup4==4.11.1",
        "requests==2.28.1",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-lexicon = certbot_dns_lexicon._internal.dns_lexicon:Authenticator",
        ],
    },
)
