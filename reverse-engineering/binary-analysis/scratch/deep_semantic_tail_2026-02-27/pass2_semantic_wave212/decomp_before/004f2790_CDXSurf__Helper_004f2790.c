/* address: 0x004f2790 */
/* name: CDXSurf__Helper_004f2790 */
/* signature: void __fastcall CDXSurf__Helper_004f2790(int param_1) */


void __fastcall CDXSurf__Helper_004f2790(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;

  iVar1 = 0;
  for (iVar2 = DAT_0083d9b0; iVar2 != 0; iVar2 = *(int *)(iVar2 + 0xa0)) {
    if (param_1 == 0) {
      iVar4 = 0;
    }
    else {
      iVar4 = param_1 + -8;
    }
    iVar3 = DAT_0083d9b0;
    if ((iVar2 == iVar4) && (iVar3 = *(int *)(iVar2 + 0xa0), iVar1 != 0)) {
      *(int *)(iVar1 + 0xa0) = *(int *)(iVar2 + 0xa0);
      iVar3 = DAT_0083d9b0;
    }
    DAT_0083d9b0 = iVar3;
    iVar1 = iVar2;
  }
  return;
}
