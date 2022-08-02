from setuptools import setup, find_packages

setup (
	name = "molnframework",
	version = "1.3",
    install_requires = ['psutil==5.6.6','Django>=1.9.4'],
	packages = find_packages(exclude=["samples","samples.*","sample","sample.*"]),
    author = "rhinodiana",
    author_email = "rhino@rhinodiano.com",
    description = "Molnframework",
)