/* address: 0x00428710 */
/* name: VFuncSlot_00_00428710 */
/* signature: int __thiscall VFuncSlot_00_00428710(void * this, void * param_1, void * param_2) */


int __thiscall VFuncSlot_00_00428710(void *this,void *param_1,void *param_2)

{
  void *unaff_EDI;

  if (((*(byte *)((int)this + 0x24) & 4) != 0) &&
     (*(int *)(*(int *)((int)this + 0x15c) + 0x198) != 0)) {
    VFuncSlot_00_00401be0(this,(int)param_1,unaff_EDI);
    return (int)param_1;
  }
  CUnitAI__Unk_00428500((int)this + -8);
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x14);
  *(undefined4 *)((int)param_1 + 4) = *(undefined4 *)((int)this + 0x18);
  *(undefined4 *)((int)param_1 + 8) = *(undefined4 *)((int)this + 0x1c);
  *(undefined4 *)((int)param_1 + 0xc) = *(undefined4 *)((int)this + 0x20);
  return (int)param_1;
}
