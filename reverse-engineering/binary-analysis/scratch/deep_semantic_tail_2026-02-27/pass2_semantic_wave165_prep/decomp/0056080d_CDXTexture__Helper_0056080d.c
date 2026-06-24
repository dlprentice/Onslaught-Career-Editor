/* address: 0x0056080d */
/* name: CDXTexture__Helper_0056080d */
/* signature: void CDXTexture__Helper_0056080d(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Helper_0056080d(void)

{
  int iVar1;
  int unaff_EBP;
  int unaff_ESI;
  int *unaff_EDI;

  *(undefined4 *)(unaff_ESI + -4) = *(undefined4 *)(unaff_EBP + -0x28);
  iVar1 = CTexture__Helper_00560b93();
  *(undefined4 *)(iVar1 + 0x6c) = *(undefined4 *)(unaff_EBP + -0x1c);
  iVar1 = CTexture__Helper_00560b93();
  *(undefined4 *)(iVar1 + 0x70) = *(undefined4 *)(unaff_EBP + -0x20);
  if ((((*unaff_EDI == -0x1f928c9d) && (unaff_EDI[4] == 3)) && (unaff_EDI[5] == 0x19930520)) &&
     ((*(int *)(unaff_EBP + -0x24) == 0 && (*(int *)(unaff_EBP + -0x2c) != 0)))) {
    __abnormal_termination();
    CDXTexture__Helper_00560a49((int)unaff_EDI);
  }
  return;
}
