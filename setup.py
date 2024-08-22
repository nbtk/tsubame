import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='tsubame',
    version='0.8.2',
    description='Quick Traceroute',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nbtk/tsubame',
    author='nbtk',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'tsubame=tsubame.traceroute:main',
        ],
    },
)
