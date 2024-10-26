import maya.cmds as cmds


def extend_keyframe(transform_path, current_time, duration):
    '''Extend the key attributes at the current time for a certain duration.'''

    all_transform_key_attr = get_keyable_attributes(transform_path)

    for new_keyframe_time in range(current_time + 1, current_time + duration + 1):
        for attr in all_transform_key_attr:
            key_value = cmds.getAttr(f"{transform_path}.{attr}", time=current_time)
            cmds.setKeyframe(f"{transform_path}.{attr}", time=(new_keyframe_time, new_keyframe_time), value=key_value)


def duplicate_camera(cam_to_dup):
    '''Duplicate the camera and copy the keyframes to the duplicate.'''
    new_cam_path = cmds.duplicate(cam_to_dup)[0]
    # When duplicating, keyframes are not copied, so copy these as well.
    cam_keyframes = get_keyframes(cam_to_dup)
    if cam_keyframes:
        copy_keyframes(cam_to_dup, new_cam_path, min(cam_keyframes), max(cam_keyframes))

    return new_cam_path


def set_keyframe_all_attr(transform_path, frame, insert):
    '''Set keyframes on all keyable attributes and the transform's shape.'''

    all_transform_key_attr = get_keyable_attributes(transform_path)

    # Set a key on everything.
    for attr in all_transform_key_attr:
        cmds.setKeyframe(transform_path, attribute=attr, insert=insert, time=(frame, frame))

    # Get the shape of the transform
    shape_path = cmds.listRelatives(transform_path, shapes=True, fullPath=True)[0]
    all_shape_key_attr = get_keyable_attributes(shape_path)

    for attr in all_shape_key_attr:
        cmds.setKeyframe(f"{shape_path}.{attr}", insert=insert, time=(frame, frame))


def get_keyable_attributes(object_path):
    '''Returns the keyable attributes on an object.'''
    return cmds.listAttr(object_path, keyable=True)


def copy_keyframes(source_object, target_object, start_time, end_time):
    '''Copies all keyframes from one maya object to another.'''

    # Copy keyframes from source to target
    if get_keyframes(source_object):
        cmds.copyKey(source_object, time=(start_time, end_time), option='keys')
        cmds.pasteKey(target_object, option='replace')


def get_keyframes(object_path):
    '''Returns all keyframes of the object from object_path.'''

    return cmds.keyframe(object_path, query=True)


def get_camera_name(camera_full_name):
    '''Get the camera name from the full cam path in outliner.'''

    camera_name = camera_full_name.split('|')[-2]

    return camera_name