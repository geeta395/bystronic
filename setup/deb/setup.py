from setuptools import setup, find_packages

setup(
    name='icpdataprocessor',
    version='0.1',
    description='Data processor for Intelligent Cutting Process',
    url='www.bystronic.com',
    author='Christoph Fahrni',
    author_email='info@bystronic.com',
    license='MIT',
    setup_requires=['wheel'],
    install_requires=[
       # 'protobuf-compiler','libprotoc-dev'
       # 'python3-onnxruntime',
       # 'onnx',
       # 'paho-mqtt'
        ],
    packages=find_packages(),
    entry_points=dict(
       # console_scripts=['rq=src.main:run']
    )
)