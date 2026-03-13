from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    model_arg = DeclareLaunchArgument(
        name='model',
        description='Percorso assoluto al file URDF del robot'
    )
    
    rvizconfig_arg = DeclareLaunchArgument(
        name='rvizconfig',
        description='Percorso assoluto al file di configurazione di rViz'
    )

    # 2. IL FIX: Diciamo esplicitamente a ROS 2 che il modello è una stringa di testo (value_type=str)
    robot_description_content = ParameterValue(
        Command(['cat ', LaunchConfiguration('model')]), 
        value_type=str
    )

    # 3. Nodo Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    # 4. Nodo Joint State Publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # 5. Nodo rViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        model_arg,
        rvizconfig_arg,
        #serve per non dire a ROS di forzare le posizioni di rviz 
        #forzando quindi rviz ad ascoltare solo
        #joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])