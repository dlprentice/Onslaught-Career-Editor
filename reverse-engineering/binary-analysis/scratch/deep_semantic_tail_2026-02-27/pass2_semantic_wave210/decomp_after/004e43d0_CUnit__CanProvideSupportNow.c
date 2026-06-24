/* address: 0x004e43d0 */
/* name: CUnit__CanProvideSupportNow */
/* signature: int __fastcall CUnit__CanProvideSupportNow(int param_1) */


int __fastcall CUnit__CanProvideSupportNow(int param_1)

{
  int iVar1;

  if ((((*(int *)(param_1 + 0x3f4) != 0) && (*(int *)(param_1 + 0x3ec) == 0)) &&
      (*(float *)(param_1 + 0x3e0) < DAT_00672fd0)) &&
     ((iVar1 = *(int *)(param_1 + 0x3d0), iVar1 != 0 &&
      ((*(int *)(param_1 + 0x3d8) < *(int *)(iVar1 + 0xc) || (*(int *)(iVar1 + 0x24) != 0)))))) {
    return 1;
  }
  return 0;
}
