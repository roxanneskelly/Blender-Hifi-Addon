# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Adding Armature related functions to the Blender Hifi Tool set
#

import bpy
import sys

from mathutils import Quaternion, Vector, Euler, Matrix

from hifi_tools.utils.bones import combine_bones, build_skeleton, retarget_armature, correct_scale_rotation, set_selected_bones_physical, remove_selected_bones_physical
from hifi_tools.armature.skeleton import structure as base_armature
from hifi_tools.utils.mmd import convert_mmd_avatar_hifi
from hifi_tools.utils.mixamo import convert_mixamo_avatar_hifi
from hifi_tools.utils.makehuman import convert_makehuman_avatar_hifi
from hifi_tools.utils.materials import make_materials_fullbright, make_materials_shadeless, convert_to_png, convert_images_to_mask

from bpy.props import StringProperty


class HifiArmaturePanel(bpy.types.Panel):
    bl_idname = "armature_toolset.hifi"
    bl_label = "Armature Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" or context.mode == "POSE"

    def draw(self, context):
        layout = self.layout
        layout.operator(HifiArmatureCreateOperator.bl_idname)
        layout.operator(HifiArmaturePoseOperator.bl_idname)
        # layout.operator(HifiArmatureRetargetPoseOperator.bl_idname)
        return None


class HifiBonePanel(bpy.types.Panel):
    bl_idname = "bones_toolset.hifi"
    bl_label = "Bones Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_ARMATURE"

    def draw(self, context):
        layout = self.layout
        layout.operator(HifiSetBonePhysicalOperator.bl_idname)
        layout.operator(HifiRemoveBonePhysicalOperator.bl_idname)
        layout.operator(HifiCombineBonesOperator.bl_idname)
        return None
    

class HifiAvatarPanel(bpy.types.Panel):
    bl_idname = "avatar_toolset.hifi"
    bl_label = "Avatar Converters"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.operator(HifiMMDOperator.bl_idname)
        layout.operator(HifiMixamoOperator.bl_idname)
        layout.operator(HifiMakeHumanOperator.bl_idname)
        return None


class HifiMaterialsPanel(bpy.types.Panel):
    bl_idname = "material_toolset.hifi"
    bl_label = "Material Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.operator(HifiMaterialFullbrightOperator.bl_idname)
        layout.operator(HifiMaterialShadelessOperator.bl_idname)

        layout.operator(HifiTexturesConvertToPngOperator.bl_idname)
        layout.operator(HifiTexturesMakeMaskOperator.bl_idname)

        return None


class HifiArmatureCreateOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_create_base_rig.hifi"
    bl_label = "Add HiFi Armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        build_skeleton()
        return {'FINISHED'}

# Remove once fst export is available


class HifiArmaturePoseOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_pose.hifi"
    bl_label = "Test Avatar Rest Pose"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        retarget_armature({'apply': False}, bpy.data.objects)

        return {'FINISHED'}


# Remove once fst export is available
class HifiSetBonePhysicalOperator(bpy.types.Operator):
    bl_idname = "bone_set_physical.hifi"
    bl_label = "Set Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return len(context.selected_bones) > 0

    def execute(self, context):
        set_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}

# Remove once fst export is available


class HifiRemoveBonePhysicalOperator(bpy.types.Operator):
    bl_idname = "bone_remove_physical.hifi"
    bl_label = "Remove Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return len(context.selected_bones) > 0

    def execute(self, context):
        remove_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}


class HifiCombineBonesOperator(bpy.types.Operator):
    bl_idname = "bone_combine.hifi"
    bl_label = "Combine Bones"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return len(context.selected_bones) > 1

    def execute(self, context):
        combine_bones(list(context.selected_bones), context.active_bone, context.active_object)
        return {'FINISHED'}


class HifiMMDOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_fix_mmd_avatar.hifi"
    bl_label = "MMD Avatar"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        convert_mmd_avatar_hifi()
        return {'FINISHED'}


class HifiMixamoOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_fix_mixamo_avatar.hifi"
    bl_label = "Mixamo Avatar"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        convert_mixamo_avatar_hifi()
        return {'FINISHED'}

class HifiMakeHumanOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_fix_makehuman_avatar.hifi"
    bl_label = "MakeHuman Avatar"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        convert_makehuman_avatar_hifi()
        retarget_armature({'apply': True}, bpy.data.objects)
        return {'FINISHED'}

class HifiMaterialFullbrightOperator(bpy.types.Operator):
    bl_idname = "materials_toolset_fullbright.hifi"
    bl_label = "Make All Fullbright"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        make_materials_fullbright(bpy.data.materials)
        return {'FINISHED'}


class HifiMaterialShadelessOperator(bpy.types.Operator):
    bl_idname = "materials_toolset_shadeless.hifi"
    bl_label = "Make All Shadeless"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        make_materials_shadeless(bpy.data.materials)
        return {'FINISHED'}


class HifiTexturesConvertToPngOperator(bpy.types.Operator):
    bl_idname = "textures_toolset_png_convert.hifi"
    bl_label = "Textures to PNG"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        convert_to_png(bpy.data.images)
        return {'FINISHED'}


class HifiTexturesMakeMaskOperator(bpy.types.Operator):
    bl_idname = "textures_toolset_mask_convert.hifi"
    bl_label = "Textures to Masked"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"

    def execute(self, context):
        convert_images_to_mask(bpy.data.images)
        return {'FINISHED'}

# -----


class HifiSaveReminderOperator(bpy.types.Operator):
    bl_idname = "hifi_error.save_file"
    bl_label = "You must save scene to a blend file first allowing for relative directories."
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label(self.bl_label)



classes = [
    HifiArmaturePanel,
    HifiMaterialsPanel,
    HifiAvatarPanel,
    HifiArmatureCreateOperator,
    HifiArmaturePoseOperator,
    HifiSetBonePhysicalOperator,
    HifiRemoveBonePhysicalOperator,
    HifiCombineBonesOperator,
    HifiMaterialFullbrightOperator,
    HifiMaterialShadelessOperator,
    HifiTexturesConvertToPngOperator,
    HifiTexturesMakeMaskOperator,
    HifiMMDOperator,
    HifiMixamoOperator,
	HifiMakeHumanOperator,
    HifiSaveReminderOperator
]


def armature_create_menu_func(self, context):
    self.layout.operator(HifiArmatureCreateOperator.bl_idname,
                         text="Add HiFi Armature",
                         icon="ARMATURE_DATA")


def armature_ui_register():
    for clz in classes:
        print(clz)
        bpy.utils.register_class(clz)

    bpy.types.INFO_MT_armature_add.append(armature_create_menu_func)


def armature_ui_unregister():
    for clz in classes:
        bpy.utils.unregister_class(clz)

    bpy.types.INFO_MT_armature_add.remove(armature_create_menu_func)


if __name__ == "__main__":
    armature_ui_register()
