/* address: 0x00481b00 */
/* name: CHud__ShutDown */
/* signature: void __fastcall CHud__ShutDown(int param_1) */


void __fastcall CHud__ShutDown(int param_1)

{
  void *pvVar1;
  int iVar2;
  int *piVar3;

  if (*(int *)(param_1 + 0x30) != 0) {
    CMissionScriptObjectCode__ClearFields();
  }
  if (*(int *)(param_1 + 0x60) != 0) {
    CDXCompass__DestroyTextures();
  }
  pvVar1 = *(void **)(param_1 + 0x60);
  if (pvVar1 != (void *)0x0) {
    CHud__Helper_0053bda0((int)pvVar1);
    OID__FreeObject(pvVar1);
    *(undefined4 *)(param_1 + 0x60) = 0;
  }
  pvVar1 = *(void **)(param_1 + 0x30);
  if (pvVar1 != (void *)0x0) {
    CMissionScriptObjectCode__ClearFields();
    OID__FreeObject(pvVar1);
    *(undefined4 *)(param_1 + 0x30) = 0;
  }
  if (*(int *)(param_1 + 0x104) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x104) + 8);
    *(undefined4 *)(param_1 + 0x104) = 0;
  }
  if (*(int *)(param_1 + 0x108) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x108) + 8);
    *(undefined4 *)(param_1 + 0x108) = 0;
  }
  if (*(int *)(param_1 + 0x10c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x10c) + 8);
    *(undefined4 *)(param_1 + 0x10c) = 0;
  }
  if (*(int *)(param_1 + 0x110) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x110) + 8);
    *(undefined4 *)(param_1 + 0x110) = 0;
  }
  if (*(int *)(param_1 + 0x114) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x114) + 8);
    *(undefined4 *)(param_1 + 0x114) = 0;
  }
  if (*(int *)(param_1 + 0x118) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x118) + 8);
    *(undefined4 *)(param_1 + 0x118) = 0;
  }
  if (*(int *)(param_1 + 0x11c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x11c) + 8);
    *(undefined4 *)(param_1 + 0x11c) = 0;
  }
  if (*(int *)(param_1 + 0x120) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x120) + 8);
    *(undefined4 *)(param_1 + 0x120) = 0;
  }
  if (*(int *)(param_1 + 0x124) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x124) + 8);
    *(undefined4 *)(param_1 + 0x124) = 0;
  }
  if (*(int *)(param_1 + 0x128) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x128) + 8);
    *(undefined4 *)(param_1 + 0x128) = 0;
  }
  if (*(int *)(param_1 + 300) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 300) + 8);
    *(undefined4 *)(param_1 + 300) = 0;
  }
  if (*(int *)(param_1 + 0x130) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x130) + 8);
    *(undefined4 *)(param_1 + 0x130) = 0;
  }
  if (*(int *)(param_1 + 0x134) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x134) + 8);
    *(undefined4 *)(param_1 + 0x134) = 0;
  }
  if (*(int *)(param_1 + 0x138) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x138) + 8);
    *(undefined4 *)(param_1 + 0x138) = 0;
  }
  if (*(int *)(param_1 + 0x13c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x13c) + 8);
    *(undefined4 *)(param_1 + 0x13c) = 0;
  }
  if (*(int *)(param_1 + 0x140) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x140) + 8);
    *(undefined4 *)(param_1 + 0x140) = 0;
  }
  if (*(int *)(param_1 + 0x148) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x148) + 8);
    *(undefined4 *)(param_1 + 0x148) = 0;
  }
  if (*(int *)(param_1 + 0x14c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x14c) + 8);
    *(undefined4 *)(param_1 + 0x14c) = 0;
  }
  if (*(int *)(param_1 + 0x150) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x150) + 8);
    *(undefined4 *)(param_1 + 0x150) = 0;
  }
  if (*(int *)(param_1 + 0x154) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x154) + 8);
    *(undefined4 *)(param_1 + 0x154) = 0;
  }
  if (*(int *)(param_1 + 0x158) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x158) + 8);
    *(undefined4 *)(param_1 + 0x158) = 0;
  }
  if (*(int *)(param_1 + 0x15c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x15c) + 8);
    *(undefined4 *)(param_1 + 0x15c) = 0;
  }
  if (*(int *)(param_1 + 0x160) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x160) + 8);
    *(undefined4 *)(param_1 + 0x160) = 0;
  }
  if (*(int *)(param_1 + 0x164) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x164) + 8);
    *(undefined4 *)(param_1 + 0x164) = 0;
  }
  if (*(int *)(param_1 + 0x168) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x168) + 8);
    *(undefined4 *)(param_1 + 0x168) = 0;
  }
  if (*(int *)(param_1 + 0x16c) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x16c) + 8);
    *(undefined4 *)(param_1 + 0x16c) = 0;
  }
  if (*(int *)(param_1 + 0x170) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x170) + 8);
    *(undefined4 *)(param_1 + 0x170) = 0;
  }
  if (*(int *)(param_1 + 0x174) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x174) + 8);
    *(undefined4 *)(param_1 + 0x174) = 0;
  }
  if (*(int *)(param_1 + 0x144) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x144) + 8);
    *(undefined4 *)(param_1 + 0x144) = 0;
  }
  if (*(int *)(param_1 + 0x1a0) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1a0) + 8);
    *(undefined4 *)(param_1 + 0x1a0) = 0;
  }
  if (*(int *)(param_1 + 0x1a4) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1a4) + 8);
    *(undefined4 *)(param_1 + 0x1a4) = 0;
  }
  if (*(int *)(param_1 + 0x1a8) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1a8) + 8);
    *(undefined4 *)(param_1 + 0x1a8) = 0;
  }
  if (*(int *)(param_1 + 0x1ac) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1ac) + 8);
    *(undefined4 *)(param_1 + 0x1ac) = 0;
  }
  if (*(int *)(param_1 + 0x1b0) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1b0) + 8);
    *(undefined4 *)(param_1 + 0x1b0) = 0;
  }
  if (*(int *)(param_1 + 0x1b4) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1b4) + 8);
    *(undefined4 *)(param_1 + 0x1b4) = 0;
  }
  if (*(int *)(param_1 + 0x1c8) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1c8) + 8);
    *(undefined4 *)(param_1 + 0x1c8) = 0;
  }
  if (*(int *)(param_1 + 0x1cc) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1cc) + 8);
    *(undefined4 *)(param_1 + 0x1cc) = 0;
  }
  if (*(int *)(param_1 + 0x1d0) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1d0) + 8);
    *(undefined4 *)(param_1 + 0x1d0) = 0;
  }
  if (*(int *)(param_1 + 0x1d4) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1d4) + 8);
    *(undefined4 *)(param_1 + 0x1d4) = 0;
  }
  if (*(int *)(param_1 + 0x1d8) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x1d8) + 8);
    *(undefined4 *)(param_1 + 0x1d8) = 0;
  }
  piVar3 = (int *)(param_1 + 0x178);
  iVar2 = 6;
  do {
    if (*piVar3 != 0) {
      CHud__Helper_004f27e0(*piVar3 + 8);
      *piVar3 = 0;
    }
    piVar3 = piVar3 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
