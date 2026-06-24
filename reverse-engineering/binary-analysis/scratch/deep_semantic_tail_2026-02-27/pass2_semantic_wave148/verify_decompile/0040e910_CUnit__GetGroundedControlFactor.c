/* address: 0x0040e910 */
/* name: CUnit__GetGroundedControlFactor */
/* signature: double __fastcall CUnit__GetGroundedControlFactor(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnit__GetGroundedControlFactor(void *param_1)

{
  int iVar1;

  iVar1 = (**(code **)(*(int *)param_1 + 0x10c))();
  if (iVar1 != 0) {
    iVar1 = HeightDelta__Below015_D4((int)param_1);
    if (iVar1 == 0) {
      return (double)_DAT_005d85d8;
    }
  }
  return (double)_DAT_005d856c;
}
