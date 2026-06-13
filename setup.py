from setuptools import setup,find_packages

setup(
    name='waves',
    version='1.0',
    description='Analyse surface waves',
#      url='needs a URL',
    author='Marc Vacher & Stéphane Perrard',
    author_email='stephane.perrard@espci.fr',
    license='GNU',
    packages=find_packages(),
    zip_safe=False,
#      package_data={'tangle': ['cl_src/*.cl']})
)
