/* address: 0x004691c0 */
/* name: CFrontEnd__ReleaseParticleHudWaypointResources */
/* signature: void __fastcall CFrontEnd__ReleaseParticleHudWaypointResources(int param_1) */


void __fastcall CFrontEnd__ReleaseParticleHudWaypointResources(int param_1)

{
  int iVar1;
  void *obj;
  int *piVar2;
  int iVar3;

  iVar3 = DAT_009c63e8;
  while (DAT_009c63e8 = iVar3, DAT_009c63e8 != 0) {
    iVar3 = *(int *)(DAT_009c63e8 + 0x68);
    CParticle__Destroy();
    *(int *)(DAT_009c63e8 + 0x68) = DAT_009c63f0;
    DAT_009c63f0 = DAT_009c63e8;
  }
  CParticleManager__ClearParticleOwnerBacklinks();
  CParticleManager__PruneDeadOwnerLinks();
  CParticleManager__CleanupHandles();
  obj = DAT_009c63f4;
  if (DAT_009c63f4 != (void *)0x0) {
    CParticleManager__Shutdown();
    OID__FreeObject(obj);
  }
  DAT_009c63f4 = (void *)0x0;
  CParticleManager__DestroyParticleList(&DAT_0082b400);
  DXParticleTexture__DestroyAll();
  piVar2 = (int *)(param_1 + 0x48);
  iVar3 = 0x56;
  do {
    if (*piVar2 != 0) {
      CHud__Helper_004f27e0(*piVar2 + 8);
      *piVar2 = 0;
    }
    piVar2 = piVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  piVar2 = (int *)(param_1 + 0x1a0);
  iVar3 = 6;
  do {
    iVar1 = *piVar2;
    if (iVar1 != 0) {
      *(int *)(iVar1 + 0x170) = *(int *)(iVar1 + 0x170) + -1;
      *piVar2 = 0;
    }
    piVar2 = piVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  CMesh__FreeUnusedAndReportLeaks();
  CWaypoint__CleanupEndLevelVBufTextures();
  CUnitAI__Helper_004f2b40();
  return;
}
