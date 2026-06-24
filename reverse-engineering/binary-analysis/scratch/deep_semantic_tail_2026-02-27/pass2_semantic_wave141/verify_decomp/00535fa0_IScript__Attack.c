/* address: 0x00535fa0 */
/* name: IScript__Attack */
/* signature: void __thiscall IScript__Attack(void * this, int param_1, void * param_2) */


void __thiscall IScript__Attack(void *this,int param_1,void *param_2)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  int unaff_EDI;

  iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
  if (iVar2 == 0) {
    CConsole__Printf(&DAT_0066f580,s_Warning__Called_Attack_with_NULL_0064fbe4);
    return;
  }
  uVar1 = *(uint *)(*(int *)((int)this + 0x10) + 0x34);
  if ((uVar1 & 0x10) == 0) {
    if ((uVar1 & 0x20000000) != 0) {
      iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
      if ((*(byte *)(iVar2 + 0x34) & 0x10) == 0) {
        iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
        if ((*(uint *)(iVar2 + 0x34) & 0x20000000) == 0) {
          return;
        }
        iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
      }
      else {
        iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
        iVar2 = *(int *)(iVar2 + 0x148);
      }
      if (iVar2 != 0) {
        (**(code **)(**(int **)((int)this + 0x10) + 0x154))(iVar2);
      }
    }
  }
  else {
    iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
    if ((*(byte *)(iVar2 + 0x34) & 0x10) == 0) {
      iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
      if ((*(uint *)(iVar2 + 0x34) & 0x20000000) == 0) {
        return;
      }
      piVar3 = (int *)(**(code **)(**(int **)param_1 + 0x40))();
      iVar2 = (**(code **)(*piVar3 + 0x128))();
    }
    else {
      iVar2 = (**(code **)(**(int **)param_1 + 0x40))();
    }
    if (iVar2 != 0) {
      CUnit__Unk_004fda20(*(void **)((int)this + 0x10),iVar2,unaff_EDI);
      return;
    }
  }
  return;
}
