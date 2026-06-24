/* address: 0x00511db0 */
/* name: CWorldPhysicsManager__FindSoundEventByNameIfEnabled */
/* signature: void __fastcall CWorldPhysicsManager__FindSoundEventByNameIfEnabled(void * param_1) */


void __fastcall CWorldPhysicsManager__FindSoundEventByNameIfEnabled(void *param_1)

{
  int iVar1;
  void *unaff_ESI;

  if (*(void **)((int)param_1 + 0x84) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x84),unaff_ESI);
    *(int *)((int)param_1 + 8) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x88) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x88),unaff_ESI);
    *(int *)((int)param_1 + 0xc) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x8c) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x8c),unaff_ESI);
    *(int *)((int)param_1 + 0x10) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x90) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x90),unaff_ESI);
    *(int *)((int)param_1 + 0x14) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x94) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x94),unaff_ESI);
    *(int *)((int)param_1 + 0x18) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x98) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x98),unaff_ESI);
    *(int *)((int)param_1 + 0x1c) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x9c) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x9c),unaff_ESI);
    *(int *)((int)param_1 + 0x20) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x7c) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x7c),unaff_ESI);
    *(int *)param_1 = iVar1;
  }
  if (*(void **)((int)param_1 + 0xa0) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0xa0),unaff_ESI);
    *(int *)((int)param_1 + 0x24) = iVar1;
  }
  if (*(void **)((int)param_1 + 0xa4) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0xa4),unaff_ESI);
    *(int *)((int)param_1 + 0x28) = iVar1;
  }
  if (*(void **)((int)param_1 + 0x80) != (void *)0x0) {
    iVar1 = CWorldPhysicsManager__Helper_004cd7a0
                      (&DAT_0082b400,*(void **)((int)param_1 + 0x80),unaff_ESI);
    *(int *)((int)param_1 + 4) = iVar1;
  }
  if (*(int *)((int)param_1 + 0xa8) != 0) {
    iVar1 = CBattleEngine__FindSoundEventByNameIfEnabled
                      (&DAT_00896988,*(int *)((int)param_1 + 0xa8),0,(int)unaff_ESI);
    *(int *)((int)param_1 + 0x34) = iVar1;
  }
  if (*(int *)((int)param_1 + 0xac) != 0) {
    iVar1 = CBattleEngine__FindSoundEventByNameIfEnabled
                      (&DAT_00896988,*(int *)((int)param_1 + 0xac),0,(int)unaff_ESI);
    *(int *)((int)param_1 + 0x38) = iVar1;
  }
  return;
}
