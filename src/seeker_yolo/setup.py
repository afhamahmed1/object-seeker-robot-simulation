from setuptools import setup

package_name = 'seeker_yolo'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Afham Ahmed',
    maintainer_email='afham12ahmed@gmail.com',
    description='YOLO object detector for the Seeker robot camera.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'yolo_node = seeker_yolo.yolo_node:main',
        ],
    },
)
