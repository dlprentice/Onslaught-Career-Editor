/* address: 0x00428770 */
/* name: VFuncSlot_01_00428770 */
/* signature: int __thiscall VFuncSlot_01_00428770(void * this, void * param_1, void * param_2) */


int __thiscall VFuncSlot_01_00428770(void *this,void *param_1,void *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  void *unaff_EDI;
  undefined4 *puVar3;

  if (((*(byte *)((int)this + 0x24) & 4) != 0) &&
     (*(int *)(*(int *)((int)this + 0x15c) + 0x198) != 0)) {
    VFuncSlot_01_00401c50(this,(int)param_1,unaff_EDI);
    return (int)param_1;
  }
  CUnitAI__Unk_00428500((int)this + -8);
  puVar2 = (undefined4 *)((int)this + 0x34);
  puVar3 = param_1;
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  return (int)param_1;
}
