/* address: 0x004fdcb0 */
/* name: CUnit__SetEngagementModeAndMaybeClearTargetReader */
/* signature: void __thiscall CUnit__SetEngagementModeAndMaybeClearTargetReader(void * this, int param_1, int param_2) */


void __thiscall
CUnit__SetEngagementModeAndMaybeClearTargetReader(void *this,int param_1,int param_2)

{
  int iVar1;

  iVar1 = *(int *)((int)this + 0x13c);
  if (iVar1 != 0) {
    if (param_1 == 1) {
      CGenericActiveReader__SetReader((void *)(iVar1 + 0xc),(void *)0x0);
      *(undefined4 *)(iVar1 + 0x10) = 0;
    }
    *(int *)((int)this + 0x210) = param_1;
    return;
  }
  *(int *)((int)this + 0x210) = param_1;
  return;
}
