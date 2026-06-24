/* address: 0x00513e20 */
/* name: CEngine__SetShaderObject */
/* signature: void __thiscall CEngine__SetShaderObject(void * this, void * shader_obj) */


void __thiscall CEngine__SetShaderObject(void *this,void *shader_obj)

{
  int iVar1;
  int iVar2;

  if ((shader_obj != DAT_0088906c) || (DAT_00889068 != -0x1234568)) {
    DAT_0088906c = shader_obj;
    DAT_00889068 = -0x1234568;
    iVar1 = **(int **)((int)this + 0x32ea0);
    iVar2 = CVertexShader__Unk_00501ba0((int)shader_obj);
    (**(code **)(iVar1 + 0x164))(*(undefined4 *)((int)this + 0x32ea0),iVar2);
    (**(code **)(**(int **)((int)this + 0x32ea0) + 0x170))
              (*(int **)((int)this + 0x32ea0),*(undefined4 *)((int)shader_obj + 0x28));
  }
  CEngine__Helper_004eba30(0);
  return;
}
