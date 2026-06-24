/* address: 0x005ab420 */
/* name: CTexture__BuildComponentPlaneRowPointers */
/* signature: void CTexture__BuildComponentPlaneRowPointers(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__BuildComponentPlaneRowPointers(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int unaff_ESI;

  iVar1 = *(int *)(unaff_ESI + 0x1ac);
  iVar2 = *(int *)(unaff_ESI + 0x140);
  iVar3 = (*(code *)**(undefined4 **)(unaff_ESI + 4))();
  iVar5 = *(int *)(unaff_ESI + 0x24);
  iVar7 = 0;
  *(int *)(iVar1 + 0x38) = iVar3;
  iVar4 = *(int *)(unaff_ESI + 0xdc);
  *(int *)(iVar1 + 0x3c) = iVar3 + iVar5 * 4;
  if (0 < iVar5) {
    piVar6 = (int *)(iVar4 + 0xc);
    do {
      iVar4 = (piVar6[6] * *piVar6) / *(int *)(unaff_ESI + 0x140);
      iVar5 = (*(code *)**(undefined4 **)(unaff_ESI + 4))();
      iVar5 = iVar5 + iVar4 * 4;
      *(int *)(*(int *)(iVar1 + 0x38) + iVar7 * 4) = iVar5;
      *(int *)(*(int *)(iVar1 + 0x3c) + iVar7 * 4) = iVar5 + (iVar2 + 4) * iVar4 * 4;
      iVar7 = iVar7 + 1;
      piVar6 = piVar6 + 0x15;
    } while (iVar7 < *(int *)(unaff_ESI + 0x24));
  }
  return;
}
