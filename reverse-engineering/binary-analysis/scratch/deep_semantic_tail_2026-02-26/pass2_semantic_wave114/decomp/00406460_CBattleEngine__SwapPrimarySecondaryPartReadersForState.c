/* address: 0x00406460 */
/* name: CBattleEngine__SwapPrimarySecondaryPartReadersForState */
/* signature: void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(int param_1) */


void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(int param_1)

{
  undefined4 uVar1;
  void *this;
  int iVar2;
  int unaff_ESI;

  iVar2 = *(int *)(param_1 + 0x260);
  if (((iVar2 == 1) || (iVar2 == 3)) && (*(int *)(param_1 + 0x5f0) == 1)) {
    uVar1 = *(undefined4 *)(param_1 + 0x5ec);
    *(undefined4 *)(param_1 + 0x5ec) = *(undefined4 *)(param_1 + 0x30);
    *(undefined4 *)(param_1 + 0x30) = uVar1;
    *(undefined4 *)(param_1 + 0x5f0) = 0;
    *(int *)(param_1 + 0x5f4) = *(int *)(param_1 + 0x70);
    *(undefined4 *)(*(int *)(param_1 + 0x70) + 8) = 0;
    *(undefined4 *)(param_1 + 0x70) = 0;
  }
  else {
    if (iVar2 != 2) {
      return;
    }
    if (*(int *)(param_1 + 0x5f0) != 0) {
      return;
    }
    uVar1 = *(undefined4 *)(param_1 + 0x5ec);
    *(undefined4 *)(param_1 + 0x5ec) = *(undefined4 *)(param_1 + 0x30);
    *(undefined4 *)(param_1 + 0x30) = uVar1;
    *(undefined4 *)(param_1 + 0x5f0) = 1;
    *(int *)(param_1 + 0x70) = *(int *)(param_1 + 0x5f4);
    if (param_1 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = param_1 + 8;
    }
    *(int *)(*(int *)(param_1 + 0x5f4) + 8) = iVar2;
    *(undefined4 *)(param_1 + 0x5f4) = 0;
  }
  iVar2 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
  if (iVar2 == 1) {
    if ((*(int *)(param_1 + 0x30) != 0) && (*(int *)(param_1 + 0x70) != 0)) {
      iVar2 = 0x14;
      do {
        CMCMech__Reset(1,0);
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
    }
    if (((*(int *)(param_1 + 0x38) != 0) &&
        (this = *(void **)(*(int *)(param_1 + 0x38) + 0x18), this != (void *)0x0)) &&
       (*(int *)(param_1 + 0x30) != 0)) {
      CInfluenceMap__SetTrackedThingAndClearCachedObject(this,*(int *)(param_1 + 0x30),unaff_ESI);
    }
  }
  return;
}
