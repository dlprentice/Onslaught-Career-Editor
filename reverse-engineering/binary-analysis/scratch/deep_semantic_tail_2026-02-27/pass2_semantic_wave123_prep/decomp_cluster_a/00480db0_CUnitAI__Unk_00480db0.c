/* address: 0x00480db0 */
/* name: CUnitAI__Unk_00480db0 */
/* signature: void __thiscall CUnitAI__Unk_00480db0(void * this, int param_1, void * param_2) */


void __thiscall CUnitAI__Unk_00480db0(void *this,int param_1,void *param_2)

{
  int iVar1;
  void *pvVar2;

  if ((param_1 != 0) && ((int *)param_1 != *(int **)((int)this + 8))) {
    iVar1 = (**(code **)(**(int **)((int)this + 8) + 0x20))(param_1);
    if (iVar1 != 0) {
      pvVar2 = *(void **)((int)this + 8);
      iVar1 = (**(code **)(*(int *)param_1 + 0x20))();
      if (iVar1 != 0) {
        if (*(int *)((int)this + 0x10) == 1) {
          CConsole__Printf(&DAT_0066f580,s_WARNING__Unexpected_collision_ch_0062cdec);
          return;
        }
        CUnitAI__Helper_00480ed0(this,(void *)param_1,pvVar2);
        *(undefined4 *)((int)this + 0x10) = 0;
      }
    }
  }
  return;
}
