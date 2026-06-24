/* address: 0x0059c070 */
/* name: CTexture__Unk_0059c070 */
/* signature: void __stdcall CTexture__Unk_0059c070(int param_1, int param_2) */


void CTexture__Unk_0059c070(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *unaff_ESI;
  int iVar5;

  iVar3 = unaff_ESI[4];
  iVar1 = unaff_ESI[2];
  iVar4 = unaff_ESI[6] * iVar1;
  iVar5 = 0;
  if (0 < iVar3) {
    do {
      iVar2 = iVar3 - iVar5;
      if (unaff_ESI[5] < iVar3 - iVar5) {
        iVar2 = unaff_ESI[5];
      }
      iVar3 = unaff_ESI[7] - (unaff_ESI[6] + iVar5);
      if (iVar3 <= iVar2) {
        iVar2 = iVar3;
      }
      iVar3 = unaff_ESI[1] - (unaff_ESI[6] + iVar5);
      if (iVar3 <= iVar2) {
        iVar2 = iVar3;
      }
      if (iVar2 < 1) {
        return;
      }
      iVar2 = iVar2 * iVar1;
      if (param_2 == 0) {
        (*(code *)unaff_ESI[0xc])
                  (param_1,unaff_ESI + 0xc,*(undefined4 *)(*unaff_ESI + iVar5 * 4),iVar4,iVar2);
      }
      else {
        (*(code *)unaff_ESI[0xd])(param_1,unaff_ESI + 0xc,*(undefined4 *)(*unaff_ESI + iVar5 * 4));
      }
      iVar3 = unaff_ESI[4];
      iVar5 = iVar5 + unaff_ESI[5];
      iVar4 = iVar4 + iVar2;
    } while (iVar5 < iVar3);
  }
  return;
}
