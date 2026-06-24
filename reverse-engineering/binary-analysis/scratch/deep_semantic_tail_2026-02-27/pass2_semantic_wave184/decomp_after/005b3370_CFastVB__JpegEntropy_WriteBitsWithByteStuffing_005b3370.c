/* address: 0x005b3370 */
/* name: CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370 */
/* signature: int __stdcall CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370(uint param_1) */


int CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370(uint param_1)

{
  int *piVar1;
  char *pcVar2;
  undefined1 *puVar3;
  char cVar4;
  int in_EAX;
  int iVar5;
  int iVar6;
  int *unaff_ESI;
  uint uVar7;

  iVar6 = unaff_ESI[3];
  if (in_EAX == 0) {
    piVar1 = (int *)unaff_ESI[8];
    *(undefined4 *)(*piVar1 + 0x14) = 0x28;
    (**(code **)*piVar1)(piVar1);
  }
  iVar6 = iVar6 + in_EAX;
  uVar7 = ((1 << ((byte)in_EAX & 0x1f)) - 1U & param_1) << (0x18U - (char)iVar6 & 0x1f) |
          unaff_ESI[2];
  do {
    if (iVar6 < 8) {
      unaff_ESI[2] = uVar7;
      unaff_ESI[3] = iVar6;
      return 1;
    }
    pcVar2 = (char *)*unaff_ESI;
    cVar4 = (char)(uVar7 >> 0x10);
    *pcVar2 = cVar4;
    *unaff_ESI = (int)(pcVar2 + 1);
    piVar1 = unaff_ESI + 1;
    *piVar1 = *piVar1 + -1;
    if (*piVar1 == 0) {
      piVar1 = *(int **)(unaff_ESI[8] + 0x18);
      iVar5 = (*(code *)piVar1[3])(unaff_ESI[8]);
      if (iVar5 == 0) {
        return 0;
      }
      iVar5 = piVar1[1];
      *unaff_ESI = *piVar1;
      unaff_ESI[1] = iVar5;
    }
    if (cVar4 == -1) {
      puVar3 = (undefined1 *)*unaff_ESI;
      *puVar3 = 0;
      *unaff_ESI = (int)(puVar3 + 1);
      piVar1 = unaff_ESI + 1;
      *piVar1 = *piVar1 + -1;
      if (*piVar1 == 0) {
        piVar1 = *(int **)(unaff_ESI[8] + 0x18);
        iVar5 = (*(code *)piVar1[3])(unaff_ESI[8]);
        if (iVar5 == 0) {
          return 0;
        }
        iVar5 = piVar1[1];
        *unaff_ESI = *piVar1;
        unaff_ESI[1] = iVar5;
      }
    }
    uVar7 = uVar7 << 8;
    iVar6 = iVar6 + -8;
  } while( true );
}
