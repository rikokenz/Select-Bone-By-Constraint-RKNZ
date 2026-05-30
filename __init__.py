bl_info = {
    "name": "Select Bone By Constraint RKNZ",
    "author": "Rikokenz",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > RKNZ",
    "description": "Select bones by constraint type in Pose Mode.",
    "category": "Animation",
}

import bpy
from bpy.props import EnumProperty


TAB = "RKNZ"


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_constraint_items(self, context):
    obj = context.active_object
    items = []
    if obj and obj.type == 'ARMATURE' and context.mode == 'POSE':
        found = set()
        for pb in obj.pose.bones:
            if pb.bone.hide:
                continue
            for c in pb.constraints:
                found.add(c.type)
        for name in sorted(found):
            items.append((name, name.title().replace("_", " "), ""))
    if not items:
        items = [('NONE', "No Constraints Found", "")]
    return items


# ── Operator ──────────────────────────────────────────────────────────────────

class POSE_OT_rknz_select_by_constraint(bpy.types.Operator):
    bl_idname = "pose.rknz_select_visible_by_constraint"
    bl_label = "Select Bones With Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object must be an armature")
            return {'CANCELLED'}
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose Mode")
            return {'CANCELLED'}
        target = context.scene.rknz_sbc_constraint
        if target == 'NONE':
            return {'CANCELLED'}
        locked = []
        for pb in obj.pose.bones:
            bone = pb.bone
            if bone.hide:
                continue
            has_constraint = any(c.type == target for c in pb.constraints)
            if not has_constraint:
                if not bone.hide_select:
                    bone.hide_select = True
                    locked.append(bone)
        bpy.ops.pose.select_all(action='SELECT')
        for bone in locked:
            bone.hide_select = False
        return {'FINISHED'}


# ── Panel ─────────────────────────────────────────────────────────────────────

class POSE_PT_rknz_select_constraint(bpy.types.Panel):
    bl_label = "Select By Constraint"
    bl_idname = "POSE_PT_rknz_select_constraint"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = TAB
    bl_context = "posemode"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "rknz_sbc_constraint", text="Constraint")
        layout.operator("pose.rknz_select_visible_by_constraint", icon='CONSTRAINT')


# ── Register ──────────────────────────────────────────────────────────────────

classes = (
    POSE_OT_rknz_select_by_constraint,
    POSE_PT_rknz_select_constraint,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.rknz_sbc_constraint = EnumProperty(
        name="Constraint",
        items=get_constraint_items,
    )


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.rknz_sbc_constraint
