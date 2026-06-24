/* address: 0x00428d50 */
/* name: VFuncSlot_22_00428d50 */
/* signature: void __fastcall VFuncSlot_22_00428d50(void * param_1) */


void __fastcall VFuncSlot_22_00428d50(void *param_1)

{
  void *this;
  int iVar1;
  void *unaff_ESI;
  char *pcVar2;

  pcVar2 = s_Activate_00623e14;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(this,(int)pcVar2,unaff_ESI);
  if (iVar1 == -1) {
    *(undefined4 *)((int)param_1 + 0x264) = 0;
    VFuncSlot_22_004fd6a0((int)param_1);
    return;
  }
  (**(code **)(*(int *)param_1 + 0xf0))(iVar1,1,0);
  return;
}
