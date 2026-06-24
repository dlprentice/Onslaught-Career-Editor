/* address: 0x00511ca0 */
/* name: CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeA */
/* signature: void __fastcall CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeA(int param_1) */


void __fastcall CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeA(int param_1)

{
  int iVar1;
  void *unaff_ESI;

  if (*(void **)(param_1 + 0x1c) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)(param_1 + 0x1c),unaff_ESI);
    *(int *)(param_1 + 4) = iVar1;
  }
  if (*(void **)(param_1 + 0x20) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)(param_1 + 0x20),unaff_ESI);
    *(int *)(param_1 + 8) = iVar1;
  }
  if (*(int *)(param_1 + 0x24) != 0) {
    iVar1 = CBattleEngine__Helper_004e1910(&DAT_00896988,*(int *)(param_1 + 0x24),0,(int)unaff_ESI);
    *(int *)(param_1 + 0xc) = iVar1;
  }
  if (*(int *)(param_1 + 0x28) != 0) {
    iVar1 = CBattleEngine__Helper_004e1910(&DAT_00896988,*(int *)(param_1 + 0x28),0,(int)unaff_ESI);
    *(int *)(param_1 + 0x10) = iVar1;
  }
  if (*(int *)(param_1 + 0x2c) != 0) {
    iVar1 = CBattleEngine__Helper_004e1910(&DAT_00896988,*(int *)(param_1 + 0x2c),0,(int)unaff_ESI);
    *(int *)(param_1 + 0x14) = iVar1;
  }
  return;
}
