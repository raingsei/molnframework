from setuptools import setup, find_packages

setup (
	name = "molnframework",
	version = "1.0",
    install_requires = ['psutil==4.1.0','Django>=1.9.4'],
	packages = find_packages(exclude=["sample","sample.*"]),
	)