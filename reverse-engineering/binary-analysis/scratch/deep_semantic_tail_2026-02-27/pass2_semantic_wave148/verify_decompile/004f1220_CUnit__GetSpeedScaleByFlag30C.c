/* address: 0x004f1220 */
/* name: CUnit__GetSpeedScaleByFlag30C */
/* signature: double __fastcall CUnit__GetSpeedScaleByFlag30C(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnit__GetSpeedScaleByFlag30C(int param_1)

{
  if (*(int *)(param_1 + 0x30c) != 0) {
    return (double)_DAT_005dbe34;
  }
  return (double)_DAT_005df464;
}
