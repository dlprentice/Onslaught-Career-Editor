/* address: 0x00421c40 */
/* name: CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40 */
/* signature: void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40(void *param_1)

{
  undefined4 local_4;

  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    *(undefined4 *)((int)param_1 + 0x124) = 0x3e4ccccd;
    *(undefined4 *)((int)param_1 + 0x14c) = 0;
    *(undefined4 *)((int)param_1 + 0x150) = 0;
    *(undefined4 *)((int)param_1 + 0x154) = 0;
    *(undefined4 *)((int)param_1 + 0x158) = local_4;
  }
  *(float *)((int)param_1 + 0x11c) = *(float *)((int)param_1 + 0x11c) * _DAT_005d9434;
  CUnit__Unk_00402fa0(param_1);
  return;
}
