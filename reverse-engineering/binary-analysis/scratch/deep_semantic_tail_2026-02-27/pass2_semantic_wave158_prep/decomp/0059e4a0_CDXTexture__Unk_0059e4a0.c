/* address: 0x0059e4a0 */
/* name: CDXTexture__Unk_0059e4a0 */
/* signature: void CDXTexture__Unk_0059e4a0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_0059e4a0(void)

{
  undefined4 *puVar1;
  undefined1 *puVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int *unaff_ESI;

  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 0xff;
  *puVar1 = puVar2 + 1;
  iVar5 = puVar1[1];
  puVar1[1] = iVar5 + -1;
  if (iVar5 + -1 == 0) {
    iVar5 = (*(code *)puVar1[3])();
    if (iVar5 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 0xdd;
  *puVar1 = puVar2 + 1;
  piVar4 = puVar1 + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    iVar5 = (*(code *)puVar1[3])();
    if (iVar5 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 0;
  *puVar1 = puVar2 + 1;
  piVar4 = puVar1 + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    iVar5 = (*(code *)puVar1[3])();
    if (iVar5 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 4;
  *puVar1 = puVar2 + 1;
  piVar4 = puVar1 + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    iVar5 = (*(code *)puVar1[3])();
    if (iVar5 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  piVar3 = (int *)unaff_ESI[6];
  puVar2 = (undefined1 *)*piVar3;
  iVar5 = unaff_ESI[0x32];
  *puVar2 = (char)((uint)iVar5 >> 8);
  *piVar3 = (int)(puVar2 + 1);
  piVar4 = piVar3 + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    iVar6 = (*(code *)piVar3[3])();
    if (iVar6 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  piVar4 = (int *)unaff_ESI[6];
  puVar2 = (undefined1 *)*piVar4;
  *puVar2 = (char)iVar5;
  *piVar4 = (int)(puVar2 + 1);
  iVar5 = piVar4[1];
  piVar4[1] = iVar5 + -1;
  if (iVar5 + -1 == 0) {
    iVar5 = (*(code *)piVar4[3])();
    if (iVar5 == 0) {
      puVar1 = (undefined4 *)*unaff_ESI;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)();
    }
  }
  return;
}
